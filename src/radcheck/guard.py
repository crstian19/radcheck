"""Pre-publish check: refuse to upload files that leak endpoints, secrets or personal data.

Hugging Face's own scan (TruffleHog on push) only flags *verified* credentials, skips LFS
files and runs after the upload. This runs before: it scans the exact files about to be
published and fails on anything that should not leave the machine.

Checks, on every text file:
- URLs whose host is not in ALLOWED_HOSTS (catches private endpoints without naming them)
- token-shaped strings (HF, OpenAI-style, GitHub, AWS, bearer tokens, private keys)
- e-mail addresses, private IP addresses, home-directory paths
- the private terms listed one per line in ~/.config/radcheck/denylist.txt (company domains,
  host names, internal model aliases...). Kept out of the repo on purpose.
- gitleaks, if installed

Usage:
    uv run --extra rocm python -m radcheck.guard <folder>
    uv run --extra rocm python -m radcheck.guard --hf Crstian19/radcheck-bench-es --type dataset
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ALLOWED_HOSTS = {
    "huggingface.co",
    "hf.co",
    "github.com",
    "arxiv.org",
    "doi.org",
    "creativecommons.org",
    "opensource.org",
    "spdx.org",
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "docs.astral.sh",
    "pytorch.org",
    "download.pytorch.org",
    "developer.mozilla.org",
    "img.shields.io",
    "citation-file-format.github.io",
    "json-schema.org",
    "www.w3.org",
    "keepachangelog.com",
    "www.sciencedirect.com",  # CARES paper
    "semver.org",
    "api.deepseek.com",  # public API, named in the benchmark's generation scripts
}
SKIP_DIRS = {
    ".git",
    ".venv",
    ".pytest_cache",
    "venv",
    "node_modules",
    "__pycache__",
    ".ruff_cache",
    "dist",
}
TEXT_SUFFIXES = {
    ".md", ".txt", ".json", ".jsonl", ".html", ".jinja", ".yaml", ".yml", ".cff",
    ".py", ".sh", ".toml", ".csv", ".cfg", ".ini",
}  # fmt: skip
DENYLIST_FILE = Path.home() / ".config" / "radcheck" / "denylist.txt"

PATTERNS = {
    "url": re.compile(r"https?://([A-Za-z0-9.-]+)"),
    "hf-token": re.compile(r"\bhf_[A-Za-z0-9]{30,}"),
    "api-key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    "github-token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    "aws-key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "bearer": re.compile(r"Bearer\s+[A-Za-z0-9._~+/-]{20,}"),
    "private-key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "private-ip": re.compile(
        r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b"
    ),
    "home-path": re.compile(r"(?:/home/|/Users/|C:\\Users\\)[A-Za-z0-9._-]+"),
}


@dataclass
class Finding:
    path: str
    line: int
    kind: str
    text: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: [{self.kind}] {self.text}"


def _denylist() -> list[str]:
    if not DENYLIST_FILE.exists():
        return []
    lines = DENYLIST_FILE.read_text(encoding="utf-8").splitlines()
    return [t.strip().lower() for t in lines if t.strip() and not t.startswith("#")]


def _host_allowed(host: str) -> bool:
    host = host.lower().rstrip(".")
    return any(host == a or host.endswith("." + a) for a in ALLOWED_HOSTS)


def scan(folder: Path) -> list[Finding]:
    deny = _denylist()
    findings = []
    for f in sorted(folder.rglob("*")):
        parts = f.relative_to(folder).parts
        if not f.is_file() or f.suffix.lower() not in TEXT_SUFFIXES or SKIP_DIRS & set(parts):
            continue
        rel = str(f.relative_to(folder))
        text = f.read_text(encoding="utf-8", errors="replace")
        for n, line in enumerate(text.splitlines(), 1):
            for kind, pattern in PATTERNS.items():
                for m in pattern.finditer(line):
                    if kind == "url" and _host_allowed(m.group(1)):
                        continue
                    findings.append(Finding(rel, n, kind, m.group(0)[:80]))
            low = line.lower()
            for term in deny:
                if term in low:
                    findings.append(Finding(rel, n, "denylist", term))
    if shutil.which("gitleaks"):
        r = subprocess.run(
            ["gitleaks", "detect", "--no-git", "--source", str(folder), "--redact", "--no-banner"],
            capture_output=True,
            text=True,
            check=False,  # exit code 1 means leaks found; handled below
        )
        if r.returncode == 1:
            findings.append(Finding(".", 0, "gitleaks", (r.stdout or r.stderr).strip()[:200]))
    return findings


def check(folder: Path) -> None:
    """Raise SystemExit with the findings if the folder is not safe to publish."""
    findings = scan(folder)
    if findings:
        print(f"guard: {len(findings)} finding(s) in {folder}, refusing to publish:")
        for finding in findings[:50]:
            print(f"  {finding}")
        sys.exit(1)
    print(f"guard: {folder} clean")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("folder", nargs="?")
    ap.add_argument("--hf", help="scan the current files of a Hub repo instead")
    ap.add_argument("--type", default="model", choices=["model", "dataset", "space"])
    args = ap.parse_args()
    if args.hf:
        from huggingface_hub import snapshot_download

        with tempfile.TemporaryDirectory() as tmp:
            snapshot_download(
                args.hf,
                repo_type=args.type,
                local_dir=tmp,
                allow_patterns=[f"*{s}" for s in TEXT_SUFFIXES],
            )
            check(Path(tmp))
    elif args.folder:
        check(Path(args.folder))
    else:
        ap.error("give a folder or --hf")


if __name__ == "__main__":
    main()

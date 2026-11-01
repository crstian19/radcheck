# %% [markdown]
# # H1: exploring CARES
#
# What the reports look like before designing the error injector. Cells use the `# %%`
# format: open this file in VS Code / Jupyter (jupytext) or run it as a script:
#
#     uv run --extra rocm python notebooks/01_explore_cares.py

# %%
import collections
import random
import re
import statistics

from datasets import load_from_disk

from radcheck.inject import candidates, split_sections

cares = load_from_disk("data/raw/cares")
texts = cares["train"]["full_text"]
n = len(texts)
print(cares)

# %% [markdown]
# ## Length and anatomical areas

# %%
words = sorted(len(t.split()) for t in texts)
print("words: median", statistics.median(words), "| p95", words[int(0.95 * n)], "| max", words[-1])
print(collections.Counter(a for row in cares["train"]["area"] for a in row).most_common())

# %% [markdown]
# ## A few reports, read by hand
#
# Reports are a single line with uppercase section headers.

# %%
rng = random.Random(1)
for t in rng.sample(texts, 3):
    print(t[:700], "...\n")

# %% [markdown]
# ## Section headers

# %%
headers = collections.Counter(
    m.strip()
    for t in texts
    for m in re.findall(r"\b([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ ]{4,}[A-ZÁÉÍÓÚÑ])\s*[:.]", t)
)
print(headers.most_common(12))


# %% [markdown]
# ## Patterns the injector relies on


# %%
def share(pred) -> str:
    return f"{100 * sum(1 for t in texts if pred(t)) / n:.0f}%"


side = re.compile(r"\b(derech|izquierd)[oa]s?\b", re.IGNORECASE)
negation = re.compile(r"\bno se (observa|aprecia|objetiva|identifica|visualiza)n?\b", re.IGNORECASE)
measure = re.compile(r"\d+(?:[.,]\d+)?\s*(mm|cm)\b")
print("has conclusion section:", share(lambda t: split_sections(t) is not None))
print("mentions a side:", share(side.search))
print("has 'no se observa'-type negation:", share(negation.search))
print("has a measurement:", share(measure.search))

# %% [markdown]
# ## Injector eligibility
#
# Share of reports where each error type creates a *verifiable* inconsistency.

# %%
eligible = collections.Counter()
for t in texts:
    for tipo in candidates(t, random.Random(0)):
        eligible[tipo] += 1
print({k: f"{100 * v / n:.0f}%" for k, v in eligible.items()})

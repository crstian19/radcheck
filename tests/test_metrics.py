from radcheck.metrics import Scores, locate
from radcheck.prompts import answer, parse_output

REPORT = "HALLAZGOS: Quiste en riñón izquierdo. CONCLUSION: Quiste en riñón derecho."
GOLD = [
    {"tipo": "lateralidad", "start": REPORT.index("derecho"), "end": REPORT.index("derecho") + 7}
]


def test_locate_tolerates_case_and_spaces():
    assert locate("riñón derecho", REPORT) is not None
    assert locate("RIÑÓN   DERECHO", REPORT) is not None
    assert locate("bazo", REPORT) is None


def test_true_positive():
    s = Scores()
    s.add(REPORT, GOLD, [{"tipo": "lateralidad", "fragmento": "Quiste en riñón derecho"}])
    out = s.summary()
    assert out["per_type"]["lateralidad"]["recall"] == 1.0
    assert out["overall"]["precision"] == 1.0


def test_wrong_type_is_fp_and_fn():
    s = Scores()
    s.add(REPORT, GOLD, [{"tipo": "medida", "fragmento": "riñón derecho"}])
    out = s.summary()
    assert out["overall"]["precision"] == 0.0
    assert out["overall"]["recall"] == 0.0


def test_false_alarm_rate_and_invalid_json():
    s = Scores()
    s.add(REPORT, [], [{"tipo": "negacion", "fragmento": "Quiste"}])
    s.add(REPORT, [], [])
    s.add(REPORT, [], None)
    out = s.summary()
    assert out["false_alarm_rate"] == round(1 / 3, 3)
    assert out["invalid_json_rate"] == round(1 / 3, 3)


def test_parse_output_roundtrip_and_think_block():
    errors = [{"tipo": "medida", "fragmento": "18 cm", "explicacion": "No coincide."}]
    assert parse_output(answer(errors)) == errors
    assert parse_output("<think>hmm {no json}</think>\n" + answer([])) == []
    assert parse_output("Aquí tienes: " + answer(errors) + " fin") == errors
    assert parse_output("no es json") is None


def test_grpo_reward():
    from radcheck.grpo import example_reward

    report = "HALLAZGOS: quiste en riñón izquierdo. CONCLUSION: quiste en riñón derecho."
    start = report.index("derecho")
    gold = [{"tipo": "lateralidad", "start": start, "end": start + 7, "counterpart": None}]
    hit = {"tipo": "lateralidad", "fragmento": "riñón derecho"}
    miss = {"tipo": "medida", "fragmento": "riñón derecho"}
    assert example_reward(report, gold, None) == -1.0
    assert example_reward(report, [], []) == 1.0
    assert example_reward(report, [], [hit]) == -1.0
    assert example_reward(report, [], [hit], clean_penalty=0.0) == 0.0
    assert example_reward(report, gold, [hit]) == 1.0
    assert example_reward(report, gold, [hit, miss]) == 2 * 0.5 * 1 / 1.5
    assert example_reward(report, gold, [miss]) == 0.0


def test_guard_flags_leaks(tmp_path):
    from radcheck.guard import scan

    (tmp_path / "ok.md").write_text("See https://huggingface.co/x and https://github.com/y.")
    (tmp_path / "bad.md").write_text(
        "endpoint https://internal.example.net/v1\nkey hf_" + "a" * 34 + "\npath /home/someone/x\n"
    )
    kinds = {f.kind for f in scan(tmp_path) if f.path == "bad.md"}
    assert {"url", "hf-token", "home-path"} <= kinds
    assert not [f for f in scan(tmp_path) if f.path == "ok.md"]

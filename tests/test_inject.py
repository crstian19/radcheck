"""Injector tests. Reports below are invented for testing; they are not patient data."""

import random

from radcheck.inject import candidates, inject, load_vocabulary, split_sections

REPORT = (
    "Edad: 60 años EXPLORACIONES: TC de abdomen con contraste. HALLAZGOS: "
    "Riñón izquierdo con quiste cortical simple de 18 mm. No se observan adenopatías "
    "retroperitoneales. Hígado de tamaño normal. "
    "CONCLUSION: Quiste renal simple en riñón izquierdo de 18 mm. "
    "No se observan adenopatías retroperitoneales."
)
NO_CONCLUSION = (
    "EXPLORACIONES: RX de tórax. HALLAZGOS: Índice cardiotorácico normal sin otros hallazgos."
)


def test_split_sections():
    sec = split_sections(REPORT)
    assert sec is not None
    assert "Riñón izquierdo" in REPORT[slice(*sec.findings)]
    assert REPORT[slice(*sec.conclusion)].strip().startswith("Quiste renal")
    assert split_sections(NO_CONCLUSION) is None


def test_candidates_cover_all_types():
    found = candidates(REPORT, random.Random(0))
    assert set(found) == {"lateralidad", "negacion", "medida"}


def test_no_candidates_without_conclusion():
    assert candidates(NO_CONCLUSION, random.Random(0)) == {}


def test_lateral_injection_creates_contradiction():
    new, err = inject(REPORT, random.Random(1), tipo="lateralidad")
    assert err.tipo == "lateralidad"
    assert new[err.start : err.end].lower() == "derecho"
    assert err.original.lower() == "izquierdo"
    assert "izquierdo" in new.lower()  # the other mention still says izquierdo


def test_negation_injection_flips_statement():
    new, _ = inject(REPORT, random.Random(2), tipo="negacion")
    assert new.count("No se observan") == 1
    assert "Se observan adenopatías" in new


def test_measure_injection_changes_value_or_unit():
    new, err = inject(REPORT, random.Random(3), tipo="medida")
    assert new[err.start : err.end] in {"180 mm", "18 cm"}
    assert "18 mm" in new  # the untouched mention remains


def test_fragment_is_exact_substring():
    rng = random.Random(4)
    for tipo in ("lateralidad", "negacion", "medida"):
        new, err = inject(REPORT, rng, tipo=tipo)
        assert err.fragmento in new
        assert err.start >= new.find(err.fragmento)


def test_single_mention_is_not_injected():
    # The side appears once, so a swap would not be verifiable from the text.
    report = (
        "HALLAZGOS: Derrame pleural derecho de pequeña cuantía. Silueta cardiaca normal. "
        "CONCLUSION: Pequeño derrame pleural."
    )
    assert "lateralidad" not in candidates(report, random.Random(0))


def test_counterpart_points_to_the_other_mention():
    rng = random.Random(5)
    for tipo, expected in (
        ("lateralidad", "izquierdo"),
        ("medida", "18 mm"),
        ("negacion", "No se observan"),
    ):
        new, err = inject(REPORT, rng, tipo=tipo)
        assert err.counterpart is not None
        s, e = err.counterpart
        assert expected.lower() in new[s:e].lower()
        assert not (s < err.end and err.start < e)  # different place than the change


def test_negation_both_directions():
    # Invented report: "sin X" in the findings, "X" affirmed in the conclusion is the error
    # direction we inject by turning "Se observa" into "No se observa" and vice versa.
    report = (
        "HALLAZGOS: Se observa derrame pleural derecho de pequeña cuantía. "
        "Ausencia de adenopatías mediastínicas. "
        "CONCLUSION: Se observa derrame pleural derecho. Sin adenopatías mediastínicas."
    )
    found = candidates(report, random.Random(0))["negacion"]
    replacements = {c.replacement for c in found}
    assert "No se" in replacements  # assertion -> negation
    assert {"Con", "Presencia"} & replacements  # negation -> assertion


def test_sin_infinitive_is_not_flipped():
    report = (
        "HALLAZGOS: Hígado sin visualizar lesiones focales. Sin visualizar lesiones esplénicas. "
        "CONCLUSION: Sin visualizar lesiones focales hepáticas."
    )
    assert all(
        c.replacement.lower() != "con"
        for c in candidates(report, random.Random(0)).get("negacion", [])
    )


def test_discordance_points_at_the_finding():
    new, err = inject(REPORT, random.Random(0), tipo="discordancia")
    assert err.tipo == "discordancia"
    assert err.fragmento in new
    assert err.start < new.index("CONCLUSION")  # reported in the findings
    assert len(new) < len(REPORT)  # a conclusion sentence was removed


def test_transcription_makes_a_non_word():
    load_vocabulary([REPORT])
    new, err = inject(REPORT, random.Random(0), tipo="transcripcion")
    changed = new[err.start : err.end]
    assert changed != err.original and changed.lower() not in REPORT.lower()
    assert err.fragmento in new


def test_inject_two_keeps_both_spans_right():
    from radcheck.inject import inject_two

    seen = 0
    for seed in range(40):
        out = inject_two(REPORT, random.Random(seed))
        if out is None:
            continue
        seen += 1
        text, errors = out
        assert len({e.tipo for e in errors}) == 2
        for e in errors:
            assert e.fragmento in text
            assert text[e.start : e.end] in e.fragmento
            if e.counterpart:
                # The counterpart is untouched text: it must still read as in the original.
                assert text[slice(*e.counterpart)] in REPORT
    assert seen > 5

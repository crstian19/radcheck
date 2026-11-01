"""Parser tests. The reports below are invented examples of the format."""

import pytest

from radcheck.radiologist import FormatError, parse

DOC = """
### Informe 001
EXPLORACIÓN: TC de tórax sin contraste.
HALLAZGOS: Nódulo pulmonar sólido de 9 mm en lóbulo superior derecho.
CONCLUSIÓN: Nódulo pulmonar de 9 mm en lóbulo superior izquierdo.

CLAVE:
- tipo: Lateralidad
  dónde: "lóbulo superior izquierdo" (conclusión)
  explicación: en hallazgos está en el lóbulo superior derecho

### Informe 002
EXPLORACIÓN: RX de tórax PA.
HALLAZGOS: Sin alteraciones pleuroparenquimatosas.
CONCLUSIÓN: Estudio dentro de la normalidad.

CLAVE: ninguno
"""


def test_parse_errors_and_clean():
    examples = parse(DOC)
    assert [ex["id"] for ex in examples] == ["rad-001", "rad-002"]
    first, second = examples
    report = first["prompt"][1]["content"]
    assert "\n" not in report
    gold = first["gold"][0]
    assert gold["tipo"] == "lateralidad"
    assert report[gold["start"] : gold["end"]] == "lóbulo superior izquierdo"
    assert second["gold"] == []
    assert second["completion"][0]["content"] == '{"errores": []}'


def test_quote_not_in_report_is_reported():
    bad = DOC.replace('"lóbulo superior izquierdo"', '"lóbulo inferior izquierdo"')
    with pytest.raises(FormatError, match="Informe 001"):
        parse(bad)


def test_missing_key_is_reported():
    with pytest.raises(FormatError, match="missing CLAVE"):
        parse("### Informe 9\nHALLAZGOS: algo.\nCONCLUSIÓN: algo.\n")

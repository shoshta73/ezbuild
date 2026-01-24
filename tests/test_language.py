from ezbuild.language import Language


def test_language_enum_c_name() -> None:
    assert Language.C.name == "C"


def test_language_enum_c_value() -> None:
    assert Language.C.value == "c"


def test_language_enum_cxx_name() -> None:
    assert Language.CXX.name == "CXX"


def test_language_enum_cxx_value() -> None:
    assert Language.CXX.value == "cxx"

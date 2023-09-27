import pytest

from mosaic_os.sourcing_platform import HarmonicGql


def test_harmonic_gql_initialises_with_env_var_successfully(tests_setup_and_teardown):
    HarmonicGql()
    assert True


def test_harmonic_gql_initialises_with_arg_successfully():
    HarmonicGql("test")
    assert True


def test_harmonic_gql_with_no_key_raises_error():
    with pytest.raises(ValueError):
        HarmonicGql()

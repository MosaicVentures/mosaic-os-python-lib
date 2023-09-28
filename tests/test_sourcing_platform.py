import pytest

from mosaic_os.sourcing_platform import HarmonicGql


# This tests if HarmonicGql initialises with an environment variable successfully
def test_harmonic_gql_initialises_with_env_var_successfully(tests_setup_and_teardown):
    HarmonicGql()
    assert True


# This tests if HarmonicGql initialises with an argument successfully
def test_harmonic_gql_initialises_with_arg_successfully():
    HarmonicGql("test")
    assert True


# This tests if HarmonicGql raises an error when no key is provided as an argument and no environment variable is set
def test_harmonic_gql_with_no_key_raises_error():
    with pytest.raises(ValueError):
        HarmonicGql()

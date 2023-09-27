from os import environ

import pytest

TEMP_ENV_VARS = {"AFFINITY_API_KEY": "test", "HARMONIC_API_KEY": "test"}


@pytest.fixture(scope="function")
def tests_setup_and_teardown():
    # Will be executed before the first test
    old_environ = dict(environ)
    environ.update(TEMP_ENV_VARS)

    yield
    # Will be executed after the last test
    environ.clear()
    environ.update(old_environ)

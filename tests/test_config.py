import pytest
from google.cloud.storage import Blob
from pytest_mock import MockerFixture

from mosaic_os.config import get_config
from mosaic_os.constants import CONFIG_BUCKET_ENV_NAME, CONFIG_OBJECT_ENV_NAME


def test_get_config_raises_error_no_config_bucket():
    with pytest.raises(ValueError) as excinfo:
        get_config(config_bucket=None, config_object_name="test")

    assert excinfo.type is ValueError
    assert excinfo.value.args[0] == (
        f"Config bucket not found in environment variables (`{CONFIG_BUCKET_ENV_NAME}`) or passed as argument"
    )


def test_get_config_raises_error_no_config_object_name():
    with pytest.raises(ValueError) as excinfo:
        get_config(config_bucket="test", config_object_name=None)

    assert excinfo.type is ValueError
    assert excinfo.value.args[0] == (
        f"Config object name not found in environment variables (`{CONFIG_OBJECT_ENV_NAME}`) or passed as argument"
    )


def test_get_config_returns_dict(mocker: MockerFixture):
    mocker.patch.object(Blob, "download_as_bytes", return_value=b'{"test": "test"}')
    config = get_config(config_bucket="test", config_object_name="test")
    assert isinstance(config, dict)
    assert config == {"test": "test"}

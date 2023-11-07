import json
from os import environ
from typing import Any

from google.cloud import storage

from mosaic_os.constants import CONFIG_BUCKET_ENV_NAME, CONFIG_OBJECT_ENV_NAME


def get_config(config_bucket: str = None, config_object_name: str = None, version: int = None) -> dict[str, Any]:
    """Gets Mosaic OS configuration stored as JSON from GCS and serialises it as a dict

    Args:
        config_bucket (str, optional): Bucket Mosaic OS configuration is located inside. Defaults to None.
        config_object_name (str, optional): Name of the config file object. Defaults to None.
        version (int, optional): Version of the configuration to retrieve.
            If not passed will retrieve latest. Defaults to None.

    Raises:
        ValueError: Raised if config_bucket or config_object_name are not passed as arguments or
            found in environment variables

    Returns:
        dict[str, Any]: Mosaic OS configuration as a dict
    """
    _config_bucket = environ.get(CONFIG_BUCKET_ENV_NAME, config_bucket)
    _config_object_name = environ.get(CONFIG_OBJECT_ENV_NAME, config_object_name)

    if _config_bucket is None:
        raise ValueError(
            f"Config bucket not found in environment variables (`{CONFIG_BUCKET_ENV_NAME}`) or passed as argument"
        )

    if _config_object_name is None:
        raise ValueError(
            f"Config object name not found in environment variables (`{CONFIG_OBJECT_ENV_NAME}`) or passed as argument"
        )

    config_object = storage.Blob(bucket=_config_bucket, name=_config_object_name, generation=version)
    config = config_object.download_as_bytes()
    return json.loads(config)

import json
from datetime import datetime
from enum import Enum

import pytest

from mosaic_os.utils import json_serializer


def test_json_serializer_with_datetime():
    dict_with_datetime = {"datetime": datetime(2021, 12, 1, 12, 0, 0)}
    result = json.dumps(dict_with_datetime, default=json_serializer)

    assert result == '{"datetime": "2021-12-01T12:00:00"}'


def test_json_serializer_with_other_type():
    class SampleEnum(Enum):
        VALUE = 1

    dict_with_other_type = {"other_type": SampleEnum.VALUE}
    with pytest.raises(TypeError, match="Type <enum 'SampleEnum'> not supported"):
        json.dumps(dict_with_other_type, default=json_serializer)

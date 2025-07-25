import datetime

import pytest

from social_network.api import models


def test_birthdate_validation() -> None:
    assert (
        models.UserDTO.validate_birthdate(
            datetime.datetime.now(tz=datetime.timezone.utc)
        )
        == datetime.datetime.now(tz=datetime.timezone.utc).date()
    )

    assert (
        models.UserDTO.validate_birthdate(
            datetime.datetime.now(tz=datetime.timezone.utc).date()
        )
        == datetime.datetime.now(tz=datetime.timezone.utc).date()
    )

    assert (
        models.UserDTO.validate_birthdate(
            str(datetime.datetime.now(tz=datetime.timezone.utc).date())
        )
        == datetime.datetime.now(tz=datetime.timezone.utc).date()
    )

    with pytest.raises(ValueError):
        assert models.UserDTO.validate_birthdate(
            datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
        )

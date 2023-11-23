from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from typing import Callable, Literal, Union
from .validators import validate_date, validate_phone_number


def _try_cast(validator: Callable[[str], str], value) -> bool:
    try:
        validator(value)
    except ValidationError:
        return False

    return True


def type_caster(value: str) -> Union[Literal['PN'], Literal['EM'], Literal['DT'], Literal['TX']]:
    """Returns FieldTemplate.FieldType.values """
    if not isinstance(value, str):
        raise TypeError("Unavailable type!")

    if _try_cast(validate_phone_number, value):
        return 'PN'
    elif _try_cast(validate_email, value):
        return 'EM'
    elif _try_cast(validate_date, value):
        return 'DT'
    else:
        return 'TX'

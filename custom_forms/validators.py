import re

from datetime import date

from django.core.exceptions import ValidationError


def validate_phone_number(value: str) -> str:
    if re.match(r'^\+7(\s\d{3}){2}(\s\d{2}){2}$', value):
        return value
    else:
        raise ValidationError("It's not a phone number in style: '+7 xxx xxx xx xx'!")


def validate_date(value: str) -> str:
    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', value):
        try:
            # split by dot, map to int and reverse for cast date(yyyy, mm, dd)
            date(*list(map(int, value.split('.')))[::-1])
        except ValueError:
            raise ValidationError("Value isn't date!")
    elif re.match(r'^\d{4}-\d{2}-\d{2}$', value):
        try:
            # split by '-', map to int for cast date(yyy, mm, dd)
            date(*list(map(int, value.split('-'))))
        except ValueError:
            raise ValidationError("Value isn't date!")
    else:
        raise ValidationError("Date format must be dd.mm.yyyy or yyyy-mm-dd!")

    return value

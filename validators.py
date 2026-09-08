"""Turn an untrusted JSON body into clean values, or explain what's wrong."""

from flask import request

from errors import ApiError

MAX_TITLE = 200
MAX_NAME = 120
MAX_COUNTRY = 80


def json_body():
    """The request body as a dict, or an ApiError explaining why it isn't."""
    if not request.is_json:
        raise ApiError(415, "Send Content-Type: application/json.")

    data = request.get_json(silent=True)

    if data is None:
        raise ApiError(400, "The request body is not valid JSON.", "MALFORMED_JSON")

    if not isinstance(data, dict):
        raise ApiError(400, "The request body must be a JSON object.", "MALFORMED_JSON")

    return data


def _text(data, key, fields, required=True, max_length=255):
    value = data.get(key)

    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            fields[key] = "This field is required."
        return None

    if not isinstance(value, str):
        fields[key] = f"Must be text, got {type(value).__name__}."
        return None

    value = value.strip()

    if len(value) > max_length:
        fields[key] = f"Must be {max_length} characters or fewer (got {len(value)})."
        return None

    return value


def _int(data, key, fields, required=True, minimum=None, maximum=None):
    value = data.get(key)

    if value is None or value == "":
        if required:
            fields[key] = "This field is required."
        return None

    if isinstance(value, bool) or not isinstance(value, (int, str)):
        fields[key] = f"Must be a whole number, got {type(value).__name__}."
        return None

    try:
        number = int(value)
    except ValueError:
        fields[key] = f"Must be a whole number, got '{value}'."
        return None

    if minimum is not None and number < minimum:
        fields[key] = f"Must be {minimum} or more."
        return None

    if maximum is not None and number > maximum:
        fields[key] = f"Must be {maximum} or less."
        return None

    return number


def _reject_unknown(data, allowed, fields):
    for key in data:
        if key not in allowed:
            fields[key] = "Unknown field."


def book_payload():
    data = json_body()
    fields = {}

    _reject_unknown(data, {"title", "author_id", "published_year"}, fields)

    title = _text(data, "title", fields, max_length=MAX_TITLE)
    author_id = _int(data, "author_id", fields, minimum=1)
    year = _int(data, "published_year", fields, required=False, minimum=1, maximum=2100)

    if fields:
        raise ApiError(422, "Some fields are invalid.", fields=fields)

    return title, year, author_id


def author_payload():
    data = json_body()
    fields = {}

    _reject_unknown(data, {"name", "country"}, fields)

    name = _text(data, "name", fields, max_length=MAX_NAME)
    country = _text(data, "country", fields, required=False, max_length=MAX_COUNTRY)

    if fields:
        raise ApiError(422, "Some fields are invalid.", fields=fields)

    return name, country

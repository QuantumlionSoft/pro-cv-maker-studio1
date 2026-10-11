from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler as drf_exception_handler


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "This document was changed elsewhere. Reload it before saving again."
    default_code = "conflict"


def api_exception_handler(exc, context):
    """Return every API error in one shape:

    {"error": {"code": str, "message": str, "fields": {field: [messages]}}}
    """
    response = drf_exception_handler(exc, context)
    if response is None:
        return None  # unexpected error: let Django log it and return 500

    data = response.data
    fields = {}
    if isinstance(data, dict) and "detail" not in data:
        fields = {key: [str(m) for m in (value if isinstance(value, list) else [value])] for key, value in data.items()}
        message = "Please correct the highlighted fields."
    elif isinstance(data, dict):
        message = str(data["detail"])
    elif isinstance(data, list):
        message = str(data[0]) if data else "Request failed."
    else:
        message = str(data)

    code = getattr(exc, "default_code", "error")
    response.data = {"error": {"code": code, "message": message, "fields": fields}}
    return response

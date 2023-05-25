from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


def prep(code):
    return code.replace("_", " ").capitalize()


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if not response or not isinstance(exc, APIException):
        return response

    response.data = {"errors": {}}
    if isinstance(exc.detail, (list, dict)):
        for field, errors in exc.detail.items():
            for error in errors:
                response.data["errors"][prep(field)] = [prep(error)]
    else:
        response.data["errors"][prep(exc.detail.code)] = [prep(exc.detail)]

    return response

from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    try:
        if response is not None and isinstance(exc, APIException):
            data = {"errors": {}}
            for field, errors in exc.detail.items():
                for error in errors:
                    data["errors"][field.capitalize()] = [error.capitalize()]
            response.data = data
    except:
        pass

    return response

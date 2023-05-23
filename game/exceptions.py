from rest_framework.exceptions import APIException


class GameSessionCreationException(APIException):
    status_code = 400
    default_detail = {'Game Session': ['Failed to create game session.']}


class GameSessionNotFoundException(APIException):
    status_code = 404
    default_detail = {'Game Session': ['Game session not found.']}


class GameSessionAlreadyStartedException(APIException):
    status_code = 400
    default_detail = {'Game Session': ['Game session has already started.']}


class NicknameAlreadyInUseException(APIException):
    status_code = 400
    default_detail = {'Player': ['Nickname already in use.']}


class MinimumPlayersNotReachedException(APIException):
    status_code = 400
    default_detail = {'Game Session': ['Minimum players not reached.']}


class NotOwnerException(APIException):
    status_code = 403
    default_detail = {'Player': ['You are not the owner of the game session.']}


class GameSessionFullException(APIException):
    status_code = 400
    default_detail = {'Game Session': ['Game session is full.']}

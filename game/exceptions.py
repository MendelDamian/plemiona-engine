from rest_framework.exceptions import APIException


class GameSessionCreationException(APIException):
    status_code = 400
    default_detail = {"Game Session": ["Failed to create game session."]}


class GameSessionNotFoundException(APIException):
    status_code = 404
    default_detail = {"Game Session": ["Game session not found."]}


class GameSessionAlreadyStartedException(APIException):
    status_code = 400
    default_detail = {"Game Session": ["Game session has already started."]}


class GameSessionNotStartedException(APIException):
    status_code = 400
    default_detail = {"Game Session": ["Game session has not started yet."]}


class NicknameAlreadyInUseException(APIException):
    status_code = 400
    default_detail = {"Player": ["Nickname already in use."]}


class MinimumPlayersNotReachedException(APIException):
    status_code = 400
    default_detail = {"Game Session": ["Minimum players not reached."]}


class NotOwnerException(APIException):
    status_code = 403
    default_detail = {"Player": ["You are not the owner of the game session."]}


class GameSessionFullException(APIException):
    status_code = 400
    default_detail = {"Game Session": ["Game session is full."]}


class BuildingNotFoundException(APIException):
    status_code = 404
    default_detail = {"Building": ["Building not found."]}


class InsufficientResourcesException(APIException):
    status_code = 400
    default_detail = {"Resources": ["You do not have enough resources."]}


class BuildingMaxLevelException(APIException):
    status_code = 400
    default_detail = {"Building level": ["This building has already reached maximum level."]}


class BuildingUpgradeException(APIException):
    status_code = 400
    default_detail = {"Building upgrade": ["Building is currently being upgraded."]}


class UnitNotFoundException(APIException):
    status_code = 404
    default_detail = {"Unit": ["Unit not found."]}


class NoUnitsToTrainException(APIException):
    status_code = 400
    default_detail = {"Units": ["You did not specify any units to train."]}


class NoUnitsToAttackException(APIException):
    status_code = 400
    default_detail = {"Units": ["You did not specify any units to attack with."]}


class CannotAttackYourselfException(APIException):
    status_code = 400
    default_detail = {"Attack": ["You cannot attack yourself."]}


class UnitsAreAlreadyBeingTrainedException(APIException):
    status_code = 400
    default_detail = {"Units": ["Units are already being trained."]}


class InsufficientUnitsException(APIException):
    status_code = 400
    default_detail = {"Units": ["You do not have enough units."]}


class GameSessionAlreadyEndedException(APIException):
    status_code = 400
    default_detail = {"Game Session": ["Game session has already ended."]}

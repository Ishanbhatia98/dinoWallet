from fastapi import HTTPException, status


class BadRequest(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class Unauthorised(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


class ResourceNotFound(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class InvalidObjectId(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class InvalidStringId(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class Forbidden(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)

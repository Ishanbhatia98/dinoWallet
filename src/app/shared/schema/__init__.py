from pydantic import BaseModel

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserLoginResponse(BaseModel):
    user_id: str
    username: str
    email: str
    jwt_token: str


class SignUpUserRequest(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
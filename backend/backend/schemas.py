from pydantic import BaseModel, ConfigDict, Field


class ExpenseSchema(BaseModel):
    title: str
    description: str = Field(min_length=1, max_length=120)
    value: int


class ExpensePublic(ExpenseSchema):
    id: int = Field(ge=1)
    model_config = ConfigDict(from_attributes=True)


class ExpenseList(BaseModel):
    expenses: list[ExpensePublic]


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: str
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class Users(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class Pagination(BaseModel):
    limit: int = Field(100, ge=0)
    offset: int = Field(0, ge=0)

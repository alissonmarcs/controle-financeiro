from pydantic import BaseModel, Field, ConfigDict

class Expense(BaseModel):
    title: str 
    description: str = Field(min_length=1, max_length=120)
    value: int

class ExpenseDBItem(Expense):
    id: int = Field(ge=1)
    model_config = ConfigDict(from_attributes=True)

class ExpenseDB(BaseModel):
    expenses: list[ExpenseDBItem]

class Message(BaseModel):
    message: str

class User(BaseModel):
    username: str
    email: str
    password: str

class CreatedUser(BaseModel):
    id: int
    username: str
    email: str
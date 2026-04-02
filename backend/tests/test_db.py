from backend.models import Expense, User
from sqlalchemy import select
from dataclasses import asdict

def test_db_create_expense(session, mock_db_time):

    with mock_db_time(model=Expense) as time:
        item = Expense(value=42, title='estacionamento', description='estacionamento do domingo')
        session.add(item)
        session.commit()

    query_result = session.scalar(select(Expense).where(Expense.title == 'estacionamento'))

    assert asdict(query_result) == {
        'id' : 1,
        'value' : 42,
        'title': 'estacionamento',
        'description' : 'estacionamento do domingo',
        'created_at' : time,
        'updated_at' : time
    }

def test_db_create_user(session, mock_db_time):

    with mock_db_time(model=User) as time:
        user = User(username="marvin", email="marvin@42.com", password="123456")
        session.add(user)
        session.commit()

    search = session.scalar(select(User).where(User.username == "marvin"))
    assert asdict(search) == {
        'id' : 1,
        'username' : 'marvin',
        'email': 'marvin@42.com',
        'password' : '123456',
        'created_at' : time,
        'updated_at' : time
    }
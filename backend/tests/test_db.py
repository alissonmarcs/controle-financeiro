from backend.models import Expense, User
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from dataclasses import asdict

import pytest


@pytest.mark.asyncio
async def test_db_create_expense(session, mock_db_time):

    with mock_db_time(model=Expense) as time:
        item = Expense(
            value=42,
            title='estacionamento',
            description='estacionamento do domingo',
        )
        session.add(item)
        await session.commit()

    query_result = await session.scalar(
        select(Expense).where(Expense.title == 'estacionamento')
    )

    assert asdict(query_result) == {
        'id': 1,
        'value': 42,
        'title': 'estacionamento',
        'description': 'estacionamento do domingo',
        'user_id': None,
        'user': None,
        'created_at': time,
        'updated_at': time,
    }


@pytest.mark.asyncio
async def test_db_create_user(session, mock_db_time):

    with mock_db_time(model=User) as time:
        user = User(
            username='marvin', email='marvin@42.com', password='123456'
        )
        session.add(user)
        await session.commit()

    search = await session.scalar(
        select(User).where(User.username == 'marvin')
    )
    assert asdict(search) == {
        'id': 1,
        'username': 'marvin',
        'email': 'marvin@42.com',
        'password': '123456',
        'expenses': [],
        'created_at': time,
        'updated_at': time,
    }


@pytest.mark.asyncio
async def test_db_user_expenses_relationship(session, mock_db_time):

    with mock_db_time(model=User) as user_time:
        user = User(
            username='marvin', email='marvin@42.com', password='123456'
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    with mock_db_time(model=Expense) as expense_time:
        expense = Expense(
            value=42,
            title='estacionamento',
            description='estacionamento do domingo',
            user_id=user.id,
        )
        # Ensure in-memory relationship stays consistent with FK assignment.
        expense.user = user
        session.add(expense)
        await session.commit()
        await session.refresh(expense)

    user_query = await session.execute(
        select(User)
        .options(selectinload(User.expenses))
        .where(User.id == user.id)
    )
    db_user = user_query.scalar_one()
    assert len(db_user.expenses) == 1
    assert db_user.expenses[0].id == expense.id
    assert db_user.expenses[0].user_id == user.id

    expense_query = await session.execute(
        select(Expense)
        .options(selectinload(Expense.user))
        .where(Expense.id == expense.id)
    )
    db_expense = expense_query.scalar_one()
    assert db_expense.user.id == user.id
    assert db_expense.user.username == user.username

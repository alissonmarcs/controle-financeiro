from dataclasses import asdict

import pytest
from sqlalchemy import select

from backend.models import Expense, UserSchema


@pytest.mark.asyncio
async def test_db_create_expense(session, mock_db_time, db_user):

    with mock_db_time(model=Expense) as time:
        item = Expense(
            user_id=db_user.id,
            value=42,
            title='estacionamento',
            description='estacionamento do domingo',
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)

    query_result = await session.scalar(
        select(Expense).where(Expense.title == 'estacionamento')
    )

    assert asdict(query_result) == {
        'id': 1,
        'value': 42,
        'title': 'estacionamento',
        'description': 'estacionamento do domingo',
        'user_id': db_user.id,
        'created_at': time,
        'updated_at': time,
    }


@pytest.mark.asyncio
async def test_db_create_user(session, mock_db_time):

    with mock_db_time(model=UserSchema) as time:
        user = UserSchema(
            username='marvin', email='marvin@42.com', password='123456'
        )
        session.add(user)
        await session.commit()

    search = await session.scalar(
        select(UserSchema).where(UserSchema.username == 'marvin')
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
async def test_db_user_expenses_relationship(session, db_user):

    expense = Expense(
        value=42,
        title='estacionamento',
        description='estacionamento do domingo',
        user_id=db_user.id,
    )
    session.add(expense)
    await session.commit()
    await session.refresh(expense)
    await session.refresh(db_user)

    user_query = await session.scalar(
        select(UserSchema).where(UserSchema.id == db_user.id)
    )

    assert user_query.expenses == [expense]

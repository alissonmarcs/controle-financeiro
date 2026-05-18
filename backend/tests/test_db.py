from dataclasses import asdict

import pytest
from sqlalchemy import select

from backend.models import Expense, User
from .factorys import UserFactory, ExpenseFactory


@pytest.mark.asyncio
async def test_db_create_expense(session, mock_db_time, db_user):

    async with mock_db_time(model=Expense) as time:
        item = await ExpenseFactory(session=session, user_id=db_user.id)
        item_created = asdict(item)

    session.expunge_all()
    query_result = await session.scalar(
        select(Expense).where(Expense.title == item_created['title'])
    )

    assert item_created == asdict(query_result)


@pytest.mark.asyncio
async def test_db_create_user(session, mock_db_time):

    async with mock_db_time(model=User) as time:
        user = await UserFactory(session=session)
        user_dict = asdict(user)
        session.expunge_all()

    search = await session.scalar(
        select(User).where(User.username == user_dict['username'])
    )

    assert user_dict == asdict(search)


@pytest.mark.asyncio
async def test_db_user_expenses_relationship(session, db_user):

    expense = await ExpenseFactory(session=session, user_id=db_user.id)
    user_id = db_user.id

    session.expunge_all()

    user_query = await session.scalar(select(User).where(User.id == user_id))

    assert user_query.expenses == [expense]

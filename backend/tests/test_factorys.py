import pytest
from sqlalchemy import select

from backend.models import UserSchema
from backend.security import verify_password

from .factorys import ExpenseFactory, UserFactory


@pytest.mark.asyncio
async def test_UserFactory_create_batch_retain_plain_passoword(session):

    few_users = await UserFactory.create_batch(5, session=session)

    for current in few_users:
        assert verify_password(current.plain_password, current.password)


@pytest.mark.asyncio
async def test_UserFactory_create_single_user_retain_plain_passoword(session):
    user = await UserFactory(session=session)
    assert verify_password(user.plain_password, user.password)


@pytest.mark.asyncio
async def test_UserFactory_create_single_user_persisted_in_db(session):
    user = await UserFactory(session=session)
    assert user.id == 1


@pytest.mark.asyncio
async def test_UserFactory_create_batch_users_persisted_in_db(session):
    users = await UserFactory.create_batch(8, session=session)
    for i, current in enumerate(users):
        assert i == current.id - 1


@pytest.mark.asyncio
async def test_ExpenseFactory_create_single_persisted_in_db(session):
    expense = await ExpenseFactory(session=session)
    assert expense.id == 1


@pytest.mark.asyncio
async def test_ExpenseFactory_should_create_user_persisted_in_db(session):
    expense = await ExpenseFactory(session=session)

    user = await session.scalar(
        select(UserSchema).where(UserSchema.id == expense.user_id)
    )

    assert user.expenses == [expense]

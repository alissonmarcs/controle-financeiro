import pytest
from backend.models import table_registry, Expense, User
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from contextlib import contextmanager
from datetime import datetime

from backend.security import get_password_hash

from backend.app import app
from backend.database import get_session

from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import pytest_asyncio


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    async with engine.begin() as transaction:
        await transaction.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as transaction:
        await transaction.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def expense(session):
    item = Expense(
        title='demo title', description='demo description', value=4242
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@pytest.fixture
def db_user(session):
    plain_password = '123456'
    user = User(
        username='spiderman',
        email='spiderman@gmail.com',
        password=get_password_hash(plain_password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    user.plain_password = plain_password
    return user


@pytest.fixture
def token(client, db_user):
    response = client.post(
        '/token',
        data={'username': db_user.email, 'password': db_user.plain_password},
    )

    return response.json()['access_token']


@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):

    def fake_time_hook(mapper, connectionn, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time

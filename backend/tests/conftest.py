from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from backend.app import app
from backend.database import get_session
from backend.models import Expense, User, table_registry
from backend.security import get_password_hash


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgress:
        pg_url = postgress.get_connection_url()
        engine = create_async_engine(pg_url)
        yield engine


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as transaction:
        await transaction.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as transaction:
        await transaction.execute(
            text('TRUNCATE TABLE "Users" RESTART IDENTITY CASCADE')
        )


@pytest_asyncio.fixture
async def expense(session, db_user):
    item = Expense(
        user_id=db_user.id,
        title='demo title',
        description='demo description',
        value=4242,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    await session.refresh(db_user)

    return item


@pytest_asyncio.fixture
async def db_user(session):
    plain_password = '123456'
    user = User(
        username='spiderman',
        email='spiderman@gmail.com',
        password=get_password_hash(plain_password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.plain_password = plain_password
    return user


@pytest_asyncio.fixture
async def token(client, db_user):
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


@pytest_asyncio.fixture
def mock_db_time():
    return _mock_db_time

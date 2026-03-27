import pytest
from backend.models import table_registry, Expense
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from contextlib import contextmanager
from datetime import datetime

from backend.app import app
from backend.database import get_session

from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient

@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
        ) 

    table_registry.metadata.create_all(engine)

    with Session (engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def expense(session):
    item = Expense(title='demo title', description='demo description', value=4242)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

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
import pytest
from backend.models import table_registry 
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from contextlib import contextmanager
from datetime import datetime

@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:') 

    table_registry.metadata.create_all(engine)

    # session = Session(engine)
    with Session (engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()

@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):

    def fake_time_hook(mapper, connectionn, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)

@pytest.fixture
def mock_db_time():
    return _mock_db_time
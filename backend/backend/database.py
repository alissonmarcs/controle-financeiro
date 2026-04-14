from backend.settings import Settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

engine = create_async_engine(Settings().DATABASE_URL)

def get_session():
    with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


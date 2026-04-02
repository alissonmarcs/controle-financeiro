from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, mapped_as_dataclass, registry


table_registry = registry()

@mapped_as_dataclass(table_registry)
class Expense:
    __tablename__ = 'Expenses'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    value: Mapped[int]
    title: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]
    created_at: Mapped[datetime] = mapped_column (
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column (
        init=False, onupdate=func.now(), server_default=func.now()
    )

@mapped_as_dataclass(table_registry)
class User:
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column (
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column (
        init=False, onupdate=func.now(), server_default=func.now()
    )


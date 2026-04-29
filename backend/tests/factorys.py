import factory

from factory.alchemy import SQLAlchemyModelFactory
from backend.security import get_password_hash
from backend.models import Expense, User


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User

    @classmethod
    async def _create(cls, model_class, *args, **kwargs):

        session_test = kwargs.pop('session')
        plain_password = kwargs.pop('plain_password', None)
        instance = model_class(*args, **kwargs)
        session_test.add(instance)
        await session_test.commit()
        await session_test.refresh(instance)

        if plain_password:
            instance.plain_password = plain_password

        return instance

    @classmethod
    async def create_batch(cls, size, **kwargs):
        return [await cls.create(**kwargs) for _ in range(size)]

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@gmail.com')
    plain_password = factory.Sequence(lambda n: f'pass{n}')
    password = factory.LazyAttribute(
        lambda obj: get_password_hash(obj.plain_password)
    )


class ExpenseFactory(factory.Factory):
    class Meta:
        model = Expense

    @classmethod
    async def _create(cls, model_class, *args, **kwargs):

        session_test = kwargs.pop('session')

        if not 'user_id' in kwargs:
            user = await UserFactory(session=session_test)
            kwargs['user_id'] = user.id

        instance = model_class(*args, **kwargs)
        session_test.add(instance)
        await session_test.commit()
        await session_test.refresh(instance)
        return instance

    @classmethod
    async def create_batch(cls, size, **kwargs):
        return [await cls.create(**kwargs) for _ in range(size)]

    value = factory.Faker('pyint', min_value=1, max_value=1000)
    title = factory.Faker('text')
    description = factory.Faker('text', max_nb_chars=119)

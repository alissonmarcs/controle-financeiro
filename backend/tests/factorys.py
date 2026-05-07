import factory
from factory.alchemy import SQLAlchemyModelFactory

from backend.models import ExpenseSchema, UserSchema
from backend.security import get_password_hash


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = UserSchema

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

    username = factory.Faker(provider='user_name', locale='pt_BR')
    email = factory.Faker(provider='email', locale='pt_BR')
    plain_password = factory.Faker(provider='password', locale='pt_BR')
    password = factory.LazyAttribute(
        lambda obj: get_password_hash(obj.plain_password)
    )


class ExpenseFactory(factory.Factory):
    class Meta:
        model = ExpenseSchema

    @classmethod
    async def _create(cls, model_class, *args, **kwargs):

        session_test = kwargs.pop('session')

        if 'user_id' not in kwargs:
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
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('sentence', nb_words=10)


class ExpensePayloadFactory(factory.Factory):
    class Meta:
        model = dict

    title = factory.Faker('sentence', locale='pt_BR', nb_words=4)
    description = factory.Faker('sentence', locale='pt_BR', nb_words=4)
    value = factory.Faker('pyint', min_value=1, max_value=1000)

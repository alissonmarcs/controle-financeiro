## o que é dataclass ?

## `from contextlib import contextmanager`

## todas as fixtures dever ter o `yield ` ?

## em `def test_db_create_expense(session, mock_db_time):`, o pytest faz o invoke das fixtures `session` e `mock_db_time` ?

Acredito que sim.

```python
# conftest.py

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
```

```python
# test_db.py

def test_db_create_expense(session, mock_db_time):

    with mock_db_time(model=Expense) as time:
        item = Expense(value=42, title='estacionamento', description='estacionamento do domingo')
        session.add(item)
        session.commit()

    query_result = session.scalar(select(Expense).where(Expense.title == 'estacionamento'))

    assert query_result.title == 'estacionamento'
    assert query_result.created_at == time
```

Veja que dentro de `test_db_create_expense`, `session` é um objeto e `mock_db_time` é uma função, e isso condiz com a definição dessas duas fixtures em `conftest.py`

Um dos motivos de `session` ser parâmetro de `test_db_create_expense`, é que a fixture `session` faz o setup de um DB de testes. Antes de `test_db_create_expense` ser executada, `session` é executada, assim `test_db_create_expense` já inicia com um DB pronto para os testes.

`mock_db_time` é uma função que retorna uma função gerenciadora de contexto. Por essa razao, `mock_db_time` deve ser executado, e dentro de um `with`. `mock_db_time` faz o setup de um hook para o evento `before_insert`, e depois remove esse hook.

## Como ver a definição de classes de pacotes ?

Exemplo:

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict( 
        env_file='.env', env_file_encoding='utf-8'
    )

    DATABASE_URL: str = Field(init=False)
```

Como localizar a definição de `SettingsConfigDict` ?

## Módulos de pacotes usam qual folder relativa para ler arquivos ?

Exemplo:

```python
# backend/backend/settings.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict( 
        env_file='.env', env_file_encoding='utf-8'
    )

    DATABASE_URL: str = Field(init=False)
```

O script python acima será executado de qual pasta ?

## É possível configurar o alembic para criar migrations para o DB em memória ?

No final da aula 04, configuramos o alembic para criar migrations.

O alembic acessa nosso esquema de tabelas (models), e a URL de conexao para o SQLite, via uma classe de config ( pacote pydantic_settings) que faz o load do nosso .env.

e criamos nossa primeira migration, que cria a tabela `Expanses` no DB.


## Nos ambientes DEV, PROD e testes, como as tabelas de DB são criadas ?

- Em DEV, são criadas através de migrations.
- Em PROD, são criadas através de migrations.
- Em testes, são criadas automaticamente por fixtures do pytest.

## Porque as sessions de DB devem ser fechadas após a response ?

## `DATABASE_URL` é parametro da classe ou da instância ?

Exemplo:

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict( 
        env_file='.env', env_file_encoding='utf-8'
    )

    DATABASE_URL: str = Field(init=False)
```


## Sempre o alembic consegue detectar as alterações de DB automaticamente ?

## Como fazer com que os testes de endpoint usem o DB em memória ?

## Quando usar o segundo e terceiro parametros de `create_engine()` ?

```python
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
        ) 
```


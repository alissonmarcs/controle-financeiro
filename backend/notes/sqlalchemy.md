No código de testes, tem um objeto representando um user da tabela `Users`

```python
# testes
@pytest_asyncio.fixture
async def expense(session, db_user):
    item = Expense(
        user_id=db_user.id, title='demo title', description='demo description', value=4242
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)

    print(f'\n\n-- AQUII -- \n\n id() de db_user nos testes: {id(db_user)}')

    return item
```

No código de implementação, tem um objeto apontando para o mesmo user que o objeto mencionado acima:

```python
# implementacao real
@router.get('/expenses/', response_model=ExpenseDB)
async def list_expenses(
    db_session: DBSession, paginator: Annotated[Pagination, Query()],
    user: CurrentUser  
):
    print(f'\n\n-- AQUII -- \n\n id() de user na implementacao: {id(user)}')
    return {'expenses': user.expenses}
```

**Os dois objetos, apesar de estarem em ambientes diferentes (testes e implementacao real) estao no mesmo endereço de memória!**

```bash
-- AQUII --

 id() de db_user nos testes: 137322505832160

# ...

-- AQUII --

 id() de user na implementacao: 137322505832160
```

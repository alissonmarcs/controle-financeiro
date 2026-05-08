from http import HTTPStatus

import pytest

from backend.schemas import ExpensePublic
from backend.security import create_access_token

from .factorys import ExpenseFactory, ExpensePayloadFactory, UserFactory


@pytest.mark.asyncio
async def test_update_user_user_not_own_exense_should_return_forbidden(
    client, session, token
):

    # user that own token is not the user that own the bellow expense
    expense = await ExpenseFactory(session=session)

    to_update_expense = ExpensePayloadFactory()

    response = client.put(
        f'/expenses/{expense.id}',
        headers={'Authorization': f'Bearer {token}'},
        json=to_update_expense,
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_create_expense_returns_201_and_created_expense(client, token):

    payload = ExpensePayloadFactory()

    response = client.post(
        '/expenses/',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    payload['id'] = 1
    assert response.json() == payload


def test_create_expense_duplicate_title_should_return_409(
    client, token, expense
):

    payload = ExpensePayloadFactory(title=expense.title)

    response = client.post(
        '/expenses/',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.CONFLICT


def test_list_expenses_should_return_empty_list_if_no_expenses(client, token):
    response = client.get(
        '/expenses/', headers={'authorization': f'bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'expenses': []}


def test_list_expenses_should_return_list_which_one_expense(
    client, expense, token
):
    expense_schema = ExpensePublic.model_validate(expense).model_dump()
    response = client.get(
        '/expenses/', headers={'authorization': f'bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'expenses': [expense_schema]}


def test_update_expense_should_return_updated_expense(client, expense, token):

    new_expense = ExpensePayloadFactory()

    response = client.put(
        '/expenses/1',
        json=new_expense,
        headers={'authorization': f'bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    new_expense['id'] = 1
    assert response.json() == new_expense


def test_update_expense_no_existent_expense_should_return_not_found(
    client, token
):

    new_expense = ExpensePayloadFactory()

    response = client.put(
        '/expenses/999',
        json=new_expense,
        headers={'authorization': f'bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


@pytest.mark.asyncio
async def test_update_expense_existing_title_should_return_conflict(
    client, expense, token, db_user, session
):

    expense_2 = await ExpenseFactory(session=session)

    to_update_first_expense = ExpensePayloadFactory(title=expense_2.title)

    response = client.put(
        f'/expenses/{expense.id}',
        json=to_update_first_expense,
        headers={'authorization': f'bearer {token}'},
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Title already exists'}


def test_delete_expense_should_return_no_contenr(client, expense, token):

    response = client.delete(
        f'/expenses/{expense.id}', headers={'authorization': f'bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Expense deleted'}


def test_delete_expense_no_existent_id_should_return_not_found(
    client, db_user, token, expense
):
    response = client.delete(
        '/expenses/42', headers={'authorization': f'bearer {token}'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Expense not found'}


@pytest.mark.asyncio
async def test_delete_expense_user_not_own_should_return_forbidden(
    client, session
):
    user1 = await UserFactory(session=session)
    user2 = await UserFactory(session=session)
    expense = await ExpenseFactory(user_id=user1.id, session=session)

    user2_jwt = create_access_token({'sub': user2.email})
    response = client.delete(
        f'/expenses/{expense.id}',
        headers={'authorization': f'bearer {user2_jwt}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

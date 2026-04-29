from http import HTTPStatus

from backend.schemas import ExpenseDBItem


from backend.security import verify_password

import pytest

from factory.alchemy import SQLAlchemyModelFactory


from .factorys import UserFactory, ExpenseFactory


@pytest.mark.asyncio
async def test_update_user_user_not_own_exense_should_return_forbidden(
    client, session, token
):

    # user that own token is not the user that own the bellow expense
    expense = await ExpenseFactory(session=session)

    response = client.put(
        f'/expenses/{expense.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'teste42',
            'description': 'teste43',
            'value': 500,
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_create_expense_returns_201_and_created_expense(client, token):
    payload = {
        'title': 'Mercado',
        'description': 'Compra semanal',
        'value': 250,
    }

    response = client.post(
        '/expenses/',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'title': 'Mercado',
        'description': 'Compra semanal',
        'value': 250,
    }


def test_create_expense_should_return_409_if_title_exists(
    client, token, expense
):

    payload = {
        'title': expense.title,
        'description': 'demo description',
        'value': 4242,
    }

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
    expense_schema = ExpenseDBItem.model_validate(expense).model_dump()
    response = client.get(
        '/expenses/', headers={'authorization': f'bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'expenses': [expense_schema]}


def test_update_expense_should_return_updated_expense(client, expense, token):
    body = {
        'title': 'mensalidade',
        'description': 'mensalidade estacionamento perto da 42',
        'value': 300,
    }
    response = client.put(
        '/expenses/1', json=body, headers={'authorization': f'bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'title': 'mensalidade',
        'description': 'mensalidade estacionamento perto da 42',
        'value': 300,
    }


def test_update_expense_no_existent_expense_should_return_not_found(
    client, expense, token
):
    body = {
        'title': 'mensalidade',
        'description': 'mensalidade estacionamento perto da 42',
        'value': 300,
    }
    response = client.put(
        '/expenses/999',
        json=body,
        headers={'authorization': f'bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_expense_existing_title_should_return_conflict(
    client, expense, token
):
    new_expense = {
        'title': 'mensalidade',
        'description': 'mensalidade estacionamento perto da 42',
        'value': 300,
    }

    response = client.post(
        '/expenses/',
        json=new_expense,
        headers={'authorization': f'bearer {token}'},
    )

    response = client.put(
        f'/expenses/{expense.id}',
        json={
            'title': 'mensalidade',
            'description': 'ida aos correios',
            'value': 200,
        },
        headers={'authorization': f'bearer {token}'},
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Title already exists'}


def test_delete_expense_should_return_no_content(client, expense):
    response = client.delete(f'/expenses/{expense.id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Expense deleted'}

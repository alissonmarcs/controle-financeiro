from http import HTTPStatus

from backend.models import Expense
from backend.schemas import ExpenseDBItem

def test_create_expense_returns_201_and_created_expense(client):
	payload = {
		'title': 'Mercado',
		'description': 'Compra semanal',
		'value': 250,
	}

	response = client.post('/expenses/', json=payload)

	assert response.status_code == HTTPStatus.CREATED
	assert response.json() == {
		'id': 1,
		'title': 'Mercado',
		'description': 'Compra semanal',
		'value': 250,
	}

def test_create_expense_should_return_409_if_title_exists(client, session, expense):

	payload = {
		"title": expense.title,
        "description": "demo description",
        "value": 4242
	}

	response = client.post('/expenses/', json=payload)
	assert response.status_code == HTTPStatus.CONFLICT

def test_list_expenses_should_return_empty_list_if_no_expenses(client):
	response = client.get('/expenses/')
	assert response.status_code == HTTPStatus.OK
	assert response.json() == {'expenses': []}

def test_list_expenses_should_return_list_whith_one_expense(client, expense):
	expense_schema = ExpenseDBItem.model_validate(expense).model_dump()
	response = client.get('/expenses/')
	assert response.status_code == HTTPStatus.OK
	assert  response.json() == {
		'expenses': [expense_schema]
	}

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

def test_update_expense_should_return_updated_expense(client, expense):
	body = {
		'title' : 'mensalidade',
		'description' : 'mensalidade estacionamento perto da 42',
		'value' : 300,
	}
	response = client.put('/expenses/1', json=body)
	assert response.status_code == HTTPStatus.OK
	assert response.json() == {
		'id': 1,
		'title' : 'mensalidade',
		'description' : 'mensalidade estacionamento perto da 42',
		'value' : 300,
	}
	
def test_update_expense_no_existent_expense_should_return_not_found(client, expense):
	body = {
		'title' : 'mensalidade',
		'description' : 'mensalidade estacionamento perto da 42',
		'value' : 300,
	}
	response = client.put('/expenses/999', json=body)
	assert response.status_code == HTTPStatus.NOT_FOUND
	assert response.json() == {
		'detail': 'User not found'
	}

def test_update_expense_existing_title_should_return_conflict(client, expense):
	new_expense = {
		'title' : 'mensalidade',
		'description' : 'mensalidade estacionamento perto da 42',
		'value' : 300,
	}

	client.post('/expenses/', json=new_expense)
	response = client.put(
		f'/expenses/{expense.id}',
		json={
			'title' : 'mensalidade',
			'description' : 'ida aos correios',
			'value' : 200,
		}
	)
	assert response.status_code == HTTPStatus.CONFLICT
	assert response.json() == {
		'detail': 'Title already exists'
	}

def test_delete_expense_should_return_no_content(client, expense):
	response = client.delete(f'/expenses/{expense.id}')
	assert response.status_code == HTTPStatus.OK
	assert response.json() == {
		'message': 'Expense deleted'
	}
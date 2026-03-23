from fastapi.testclient import TestClient

from backend.app import app
from backend.routers.expenses import expenses_fake_db

client = TestClient(app)


def setup_function() -> None:
	expenses_fake_db.clear()


def test_create_expense_returns_201_and_created_expense() -> None:
	payload = {
		'title': 'Mercado',
		'description': 'Compra semanal',
		'value': 250,
	}

	response = client.post('/expenses/', json=payload)

	assert response.status_code == 201
	assert response.json() == {
		'id': 1,
		'title': 'Mercado',
		'description': 'Compra semanal',
		'value': 250,
	}
	assert len(expenses_fake_db) == 1


def test_create_expense_with_invalid_description_returns_422() -> None:
	payload = {
		'title': 'Transporte',
		'description': '',
		'value': 35,
	}

	response = client.post('/expenses/', json=payload)

	assert response.status_code == 422
	assert len(expenses_fake_db) == 0


def test_create_expense_increments_id() -> None:
	first_payload = {
		'title': 'Almoco',
		'description': 'Restaurante',
		'value': 42,
	}
	second_payload = {
		'title': 'Internet',
		'description': 'Mensalidade',
		'value': 120,
	}

	first_response = client.post('/expenses/', json=first_payload)
	second_response = client.post('/expenses/', json=second_payload)

	assert first_response.status_code == 201
	assert second_response.status_code == 201
	assert first_response.json()['id'] == 1
	assert second_response.json()['id'] == 2
	assert len(expenses_fake_db) == 2


def test_list_expenses_returns_empty_list() -> None:
	response = client.get('/expenses/')

	assert response.status_code == 200
	assert response.json() == {'expenses': []}


def test_list_expenses_returns_created_expenses() -> None:
	payloads = [
		{
			'title': 'Mercado',
			'description': 'Compra do mes',
			'value': 300,
		},
		{
			'title': 'Luz',
			'description': 'Conta de energia',
			'value': 180,
		},
	]

	for payload in payloads:
		create_response = client.post('/expenses/', json=payload)
		assert create_response.status_code == 201

	response = client.get('/expenses/')

	assert response.status_code == 200
	assert response.json() == {
		'expenses': [
			{
				'id': 1,
				'title': 'Mercado',
				'description': 'Compra do mes',
				'value': 300,
			},
			{
				'id': 2,
				'title': 'Luz',
				'description': 'Conta de energia',
				'value': 180,
			},
		],
	}


def test_update_expense_returns_updated_expense() -> None:
	create_payload = {
		'title': 'Academia',
		'description': 'Mensalidade',
		'value': 99,
	}
	update_payload = {
		'title': 'Academia Premium',
		'description': 'Plano anual',
		'value': 120,
	}

	create_response = client.post('/expenses/', json=create_payload)
	assert create_response.status_code == 201

	update_response = client.put('/expenses/1', json=update_payload)

	assert update_response.status_code == 200
	assert update_response.json() == {
		'id': 1,
		'title': 'Academia Premium',
		'description': 'Plano anual',
		'value': 120,
	}
	assert len(expenses_fake_db) == 1
	assert expenses_fake_db[0].title == 'Academia Premium'
	assert expenses_fake_db[0].description == 'Plano anual'


def test_update_expense_returns_404_when_not_found() -> None:
	update_payload = {
		'title': 'Agua',
		'description': 'Conta de agua',
		'value': 70,
	}

	response = client.put('/expenses/999', json=update_payload)

	assert response.status_code == 404
	assert response.json() == {'detail': 'Expense not found'}


def test_delete_expense_returns_204_and_removes_item() -> None:
	payload = {
		'title': 'Streaming',
		'description': 'Assinatura mensal',
		'value': 45,
	}

	create_response = client.post('/expenses/', json=payload)
	assert create_response.status_code == 201
	assert len(expenses_fake_db) == 1

	delete_response = client.delete('/expenses/1')

	assert delete_response.status_code == 204
	assert delete_response.text == ''
	assert len(expenses_fake_db) == 0


def test_delete_expense_returns_404_when_not_found() -> None:
	response = client.delete('/expenses/999')

	assert response.status_code == 404
	assert response.json() == {'detail': 'Expense not found'}

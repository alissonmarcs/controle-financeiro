Toda Expense precia ter um user atrelado.
Os endpoints `/expenses` precisam ser modificados para receber esse esse user nos headers.


## Como rodar testes

Termina a execução na primeira falha, o output terá apenas o resultado recebido e o esperado:

```bash
pytest -q -x --no-header
```

Roda somente o teste que falhou na ultima execução:

```bash
pytest --lf -q -x --no-header
```
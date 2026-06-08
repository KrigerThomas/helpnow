# HelpNOW 🔧

**Plataforma web para solicitação rápida de serviços domésticos.**

Conecta clientes que precisam de serviços (elétrica, hidráulica, limpeza, TI, pintura) a prestadores autônomos cadastrados na plataforma, simplificando o processo de contratação sem depender de indicações informais.

> Projeto desenvolvido para a disciplina de Desenvolvimento Web — UVV  
> **Grupo:** Antony Novais, Heitor Rodrigues e Thomás Kriger

---

## Funcionalidades do MVP

- Cadastro de **clientes** e **prestadores** com papéis distintos
- Prestadores cadastram serviços com categoria, descrição, preço e localidade
- Clientes buscam profissionais por **categoria** e/ou **localidade**
- Clientes enviam solicitações de serviço com mensagem e endereço
- Prestadores visualizam, **aceitam ou recusam** solicitações recebidas
- Clientes marcam serviços como **concluídos** e deixam uma **avaliação (1–5)**
- Edição de perfil para ambos os tipos de usuário

---

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.11 · Flask · Flask-Login · Flask-WTF |
| ORM | SQLAlchemy 2.x · Flask-SQLAlchemy |
| Frontend | Jinja2 · Bulma 0.9.4 · Font Awesome 6 |
| Banco de dados | SQLite (dev/test) |
| Testes | pytest · pytest-flask · pytest-cov |
| Automação | Invoke (`tasks.py`) |

---

## Como rodar o projeto

### 1. Clonar e criar o ambiente virtual

```bash
git clone <url-do-repositorio>
cd helpnow
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

### 2. Instalar dependências

```bash
pip install -e ".[dev,test]"
```

> Ou usar o Invoke: `invoke install`

### 3. Criar o banco de dados

```bash
flask create-db
```

### 4. (Opcional) Popular com dados de exemplo

```bash
invoke seed-dev
```

Cria 3 usuários de teste:
- **Cliente:** `thomas@email.com` / `123456`
- **Prestador:** `heitor@email.com` / `123456`
- **Prestador:** `antony@email.com` / `123456`

### 5. Rodar a aplicação

```bash
invoke run
# ou diretamente:
flask run
```

Acesse: [http://localhost:5000](http://localhost:5000)

---

## Rodar os testes

```bash
invoke test
# ou diretamente:
pytest -v
```

---

## Estrutura do projeto

```
helpnow/
├── app.py                  # Application factory (create_app)
├── pyproject.toml          # Dependências e configuração do projeto
├── tasks.py                # Automação com Invoke
├── .env.dev / .env.test    # Variáveis de ambiente por contexto
│
├── helpnow/
│   ├── ext/                # Extensões Flask (db, login, config, cli...)
│   ├── models/             # Modelos SQLAlchemy (User, Servico, Solicitacao...)
│   ├── views/              # Blueprints e rotas (main, auth, perfil)
│   └── forms/              # Formulários WTForms (auth, servico, perfil...)
│
├── templates/main/         # Templates Jinja2
├── static/css/             # CSS customizado
└── tests/                  # Testes automatizados com pytest
```

---

## Variáveis de ambiente

O projeto usa arquivos `.env.<ambiente>` carregados automaticamente pelo `invoke`:

| Arquivo | Uso |
|---|---|
| `.env.dev` | Desenvolvimento local |
| `.env.test` | Execução dos testes |
| `.env.prod` | Produção |

Variáveis principais: `SECRET_KEY`, `DATABASE_URL`, `FLASK_DEBUG`.

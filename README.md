<div align="center">

# HelpNOW 🔧

**Plataforma web para solicitação rápida de serviços domésticos**

Conecta clientes que precisam de serviços (elétrica, hidráulica, limpeza, TI, pintura) a prestadores autônomos, simplificando a contratação sem depender de indicações informais.

![Testes](https://github.com/KrigerThomas/helpnow/actions/workflows/tests.yml/badge.svg)
&nbsp;
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
&nbsp;
![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)
&nbsp;
![Licença](https://img.shields.io/badge/Licença-MIT-22c55e)

<br>

Projeto desenvolvido para a disciplina de **Desenvolvimento Web — UVV**  
**Grupo:** Antony Novais · Heitor Rodrigues · Thomás Kriger

</div>

---

## Capturas de tela

<table>
  <tr>
    <td align="center"><b>Página inicial</b></td>
    <td align="center"><b>Busca de profissionais</b></td>
  </tr>
  <tr>
    <td><img src=".github/images/tela_index.png" alt="Página inicial" width="100%"/></td>
    <td><img src=".github/images/tela_busca.png" alt="Busca" width="100%"/></td>
  </tr>
  <tr>
    <td align="center"><b>Painel do prestador</b></td>
    <td align="center"><b>Perfil do usuário</b></td>
  </tr>
  <tr>
    <td><img src=".github/images/tela_prestador.png" alt="Painel do prestador" width="100%"/></td>
    <td><img src=".github/images/tela_perfil.png" alt="Perfil" width="100%"/></td>
  </tr>
</table>

---

## Funcionalidades

- Cadastro de **clientes** e **prestadores** com papéis distintos
- Prestadores cadastram serviços com categoria, descrição, preço e localidade
- Clientes buscam profissionais por **categoria** e/ou **localidade**
- Envio de solicitações com mensagem e endereço
- Prestadores **aceitam ou recusam** solicitações recebidas
- Clientes marcam serviços como **concluídos** e deixam uma **avaliação (1–5)**
- Edição de perfil para ambos os tipos de usuário

---

## Stack tecnológica

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.11 · Flask · Flask-Login · Flask-WTF |
| ORM | SQLAlchemy 2.x · Flask-SQLAlchemy |
| Frontend | Jinja2 · Bulma 0.9.4 · Font Awesome 6 |
| Banco de dados | SQLite (dev/test) |
| Testes | pytest · pytest-flask · pytest-cov |
| Automação | Invoke (`tasks.py`) |

---

## Diagrama do banco de dados

![Diagrama ER](docs/er_diagram.png)

---

## Como rodar o projeto

### Pré-requisitos

- Python 3.9 ou superior
- pip

### 1. Clone e crie o ambiente virtual

```bash
git clone https://github.com/KrigerThomas/helpnow.git
cd helpnow

python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### 2. Configure as variáveis de ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env.dev

# Abra .env.dev e preencha ao menos a SECRET_KEY
```

> Gere uma SECRET_KEY segura:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 3. Instale as dependências

```bash
pip install -e ".[dev,test]"

# Ou via Invoke:
invoke install
```

### 4. Crie o banco de dados

```bash
flask create-db
```

### 5. (Opcional) Popule com dados de exemplo

```bash
invoke seed-dev
```

Cria 3 usuários de teste — todos com senha `123456`:

| Tipo | E-mail |
|---|---|
| Cliente | `thomas@email.com` |
| Prestador | `heitor@email.com` |
| Prestador | `antony@email.com` |

### 6. Rode a aplicação

```bash
invoke run
# ou: flask run
```

Acesse: [http://localhost:5000](http://localhost:5000)

---

## Testes

```bash
invoke test
# ou: pytest -v
```

Os testes cobrem rotas públicas, formulários, autenticação e proteção de rotas.

---

## Estrutura do projeto

```
helpnow/
├── app.py                    # Application factory (create_app)
├── pyproject.toml            # Dependências e metadados
├── tasks.py                  # Automação com Invoke
├── .env.example              # Template de variáveis de ambiente
├── LICENSE
├── README.md
│
├── .github/
│   ├── images/               # Screenshots do projeto (README)
│   └── workflows/
│       └── tests.yml         # CI — roda os testes a cada push
│
├── scripts/
│   ├── gerar_er.py           # Gerador do diagrama ER
│   └── make_env.py           # Setup de ambiente (Windows)
│
├── docs/
│   └── er_diagram.png        # Diagrama do banco de dados
│
├── helpnow/
│   ├── ext/                  # Extensões Flask (db, login, config, cli…)
│   ├── models/               # Modelos SQLAlchemy (User, Servico, Solicitacao…)
│   ├── views/                # Blueprints e rotas (main, auth, perfil)
│   └── forms/                # Formulários WTForms (auth, servico, perfil…)
│
├── templates/main/           # Templates Jinja2
├── static/css/               # CSS customizado (Bulma base)
└── tests/                    # Testes automatizados (pytest)
```

---

## Variáveis de ambiente

Copie `.env.example` para `.env.dev` e preencha — **nunca suba arquivos `.env` reais**.

| Arquivo | Uso |
|---|---|
| `.env.dev` | Desenvolvimento local |
| `.env.test` | Testes automatizados |
| `.env.prod` | Produção |

---

## Licença

MIT License — veja [LICENSE](LICENSE) para detalhes.

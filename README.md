# Py Bank API

## Descrição do Projeto

O **Py Bank API** é uma aplicação bancária online desenvolvida com **Flask** e **PostgreSQL**, oferecendo funcionalidades essenciais para gerenciamento de contas e transações financeiras.

A aplicação possui os seguintes recursos:

✅ **Cadastro e Autenticação de Usuários**: Criação de contas e login seguro com autenticação JWT.  
✅ **Gerenciamento de Contas Bancárias**: Criação de contas, consulta de saldo e histórico de transações.  
✅ **Movimentações Financeiras**: Depósitos, saques e transferências entre contas.  
✅ **Histórico de Transações**: Registro detalhado de todas as operações.  
✅ **Notificações por E-mail**: Alertas automáticos para eventos importantes.  
✅ **Segurança**: Implementação de **JWT**, **proteção contra fraudes** e **limites de transação**.  

---

## Tecnologias Utilizadas

- ![Python](https://img.shields.io/badge/-Python-black?style=flat-square&logo=python)
- ![Flask](https://img.shields.io/badge/-Flask-black?style=flat-square&logo=flask)
- ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-black?style=flat-square&logo=postgresql)
- ![JWT](https://img.shields.io/badge/-JWT-black?style=flat-square&logo=json-web-tokens)
- ![HTML](https://img.shields.io/badge/-HTML-black?style=flat-square&logo=html5)
- ![Bootstrap](https://img.shields.io/badge/-Bootstrap-black?style=flat-square&logo=bootstrap)

---

## Instalação e Configuração

### 1. Clonar o repositório
```bash
git clone https://github.com/zeneiltongpdev/PyBankSystem.git
cd PyBankSystem
```
### 2. Criar e ativar o ambiente virtual
```bash
python -m venv venv  
source venv/bin/activate  # Linux/macOS  
venv\Scripts\activate  # Windows  
```

### 3. Instalar as dependências
```bash
pip install -r requirements.txt  
```

### 4. Configurar variáveis de ambiente
*Crie um arquivo `.env` e defina as seguintes variáveis:*
```ini
SECRET_KEY="sua-chave-secreta"
DATABASE_URL="postgresql://usuario:senha@localhost:5432/mybank"
MAIL_SERVER="smtp.gmail.com"
MAIL_PORT=587
MAIL_USERNAME="seu-email@gmail.com"
MAIL_PASSWORD="sua-senha"
MAIL_USE_TLS=True
```

### 5. Criar e migrar o banco de dados
```bash
flask db init  
flask db migrate -m "Inicializando banco"  
flask db upgrade  
```

### 6. Executar a API
```bash
app.py run
```
A API estará disponível em: **http://127.0.0.1:5000/docs**

### Endpoints Disponíveis
🔐 **Autenticação**
- `POST /register` → Cria um novo usuário
- `POST /login` → Retorna um token JWT

🏦 **Gerenciamento de Conta**
- `GET /account` → Obtém informações da conta
- `GET /balance` → Consulta o saldo atual

💰 **Transações**
- `POST /deposit` → Realiza um depósito
- `POST /withdraw` → Realiza um saque
- `POST /transfer` → Transfere valores entre contas

📜 Extras
- `GET /transactions` → Histórico de transações
- `POST /notify` → Envia notificações por e-mail

### Testando a API
Para testar os endpoints, você pode utilizar `Postman`, `Thunder Client`, ou a ferramenta CLI `curl`.

Exemplo de requisição de login:
```bash
curl -X POST http://127.0.0.1:5000/login -H "Content-Type: application/json" -d '{"username": "userHere", "password": "passHere"}'
```

### Futuras Melhorias
- Implementação de limites personalizados de transação
- Suporte para pix e boletos
- Dashboard frontend para acompanhamento das transações

### Autor
👤 **[Zeneilton GP Dev](https://github.com/zeneiltongpdev)**

📜 **Licença: [MIT License]()**

🚀 **Contribuições são bem-vindas!**

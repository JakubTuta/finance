# Finance

## 🚀 Overview
**Finance** is a comprehensive financial management tool that helps users track and manage their expenses. It allows you to add subscriptions and singular finance items to understand your spending patterns. The app leverages AI models to help you make better financial decisions while ensuring your sensitive financial data stays private.

Check it out [here](https://finance-9795f.web.app)

---

## 🌟 Features
- **Expense Tracking**: Easily log subscriptions and one-time purchases to monitor your spending.
- **Financial Analysis**: Get insights into your spending habits and financial patterns.
- **AI-Powered Recommendations**: Receive personalized advice for better financial decisions.
- **MongoDB Database**: Stores all financial data efficiently and reliably.
- **Local Deployment**: Process your financial data securely on your own machine with no cloud dependency.
- **Privacy First**: Your financial information stays local, giving you complete control.
- **User friendly UI**: Simple and intuitive front-end app for managing your finances

---

## 🛠️ Getting Started

### Prerequisites
- [Docker](https://www.docker.com/) installed on your machine

## Running app with docker
#### 1. Clone the repository:
```bash
git clone https://github.com/JakubTuta/finance.git

cd finance
```

#### 2. Starting app
```bash
docker-compose up -d
```

Fastapi server runs on `http://localhost:8000` \
Nuxt web app runs on `http://localhost:3000` \
MongoDB runs on `http://localhost:27017`

## Running each module separately

### 1. Starting server
```bash
cd backend
```

Create virtual environment
```bash
python -m venv venv
```

Run virtual environment
```bash
# on Windows
venv/Scripts/activate

# on MacOS / Linux
source venv/bin/activate
```

Install the modules:

```bash
pip install -r requirements.txt
```

Create `.env` file in `backend` directory with following content (check .env.example for reference):
```bash
ACCESS_SECRET_KEY: Generate SHA256 key
REFRESH_SECRET_KEY: Generate SHA256 key
DATABASE_USERNAME: Database username
DATABASE_PASSWORD: Database password
DATABASE_NAME: Database name
DATABASE_PORT: Database port
LOCAL_DATABASE_HOST: MongoDB url (for example hosted on docker)
GEMINI_API_KEY: Your gemini api key

# Optional
PRODUCTION_DATABASE_HOST: Production MongoDB url (for example hosted on mongodb atlas)
IS_PRODUCTION: true if production, false if local
```

Make sure the mongodb database is running on `http://localhost:27017`

Now you can run server

```bash
fastapi run main.py
```

Fastapi server is running on `http://localhost:8000`

### 2. Starting Nuxt app
```bash
cd frontend
```

Install the dependencies:

```bash
# replace npm with any package manager
npm install
```

```bash
# # replace npm with any package manager
npm run dev
```

Nuxt app is running on `http://localhost:3000`
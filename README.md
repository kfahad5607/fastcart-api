# FastCart API

FastCart API is a scalable e-commerce backend built using FastAPI. It currently supports managing products and orders with the following features:

- List products with pagination, sorting, and filtering by search query
- Create a new product
- Create a new order

## Tech Stack
- **FastAPI** - High-performance Python web framework for building APIs
- **PostgreSQL** - Relational database management system
- **SQLAlchemy & SQLModel** - ORM for database interactions
- **Alembic** - Database migrations
- **Docker & Docker Compose** - Containerized deployment

## System Requirements
Before installing, ensure you have the following installed:
- **Git** - Version control system ([Download Git](https://git-scm.com/downloads))
- **Docker & Docker Compose** - For containerized setup ([Download Docker](https://www.docker.com/get-started))
- **Python 3.8+** - Required for local development ([Download Python](https://www.python.org/downloads/))

## Installation

### 1. Clone the Repository
```sh
git clone https://github.com/kfahad5607/fastcart-api.git
cd fastcart-api
```

---

## Installation Option 1: Virtual Environment (For Development)
This approach runs the application locally while using Docker for the database.

### 1. Create a Virtual Environment
```sh
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 2. Install Dependencies
```sh
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file based on `.env.example` and update credentials as needed.

> **Important:** Keep `DB_HOST=localhost` when using this setup.

Example `.env` file:
```
APP_NAME="FastCart API"
DEBUG_MODE=True
CORS_ORIGINS=http://localhost:5173
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=fastcart_db

TEST_DB_HOST=localhost
TEST_DB_USER=testuser
TEST_DB_PASSWORD=testpass
TEST_DB_NAME=test_db
TEST_DB_PORT=5433
```

### 4. Start the Database
> **Note:** Comment out the `app` service in `docker-compose.yml` before starting the database.

```sh
docker-compose up -d
```

### 5. Run Database Migrations
```sh
alembic upgrade head
```

### 6. Seed the Database (Optional)
```sh
python3 -m seeds.products -n 200
python3 -m seeds.orders -n 200
```

### 7. Start the API Server
```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 8. Access the API
Visit [http://localhost:8000/docs](http://localhost:8000/docs) to explore API endpoints.

### 9. Run Tests
```sh
python3 -m pytest -v
```

---

## Installation Option 2: Docker Compose
This approach runs the entire application, including FastAPI and PostgreSQL, inside Docker containers.

### 1. Set Up Environment Variables
Create a `.env` file based on `.env.example`.

> **Important:** Keep `DB_HOST=db` when using Docker Compose.

### 2. Ensure `app` Service is Active in `docker-compose.yml`
Make sure the `app` service is **not commented out** before running the application.

### 3. Run the Application
```sh
docker-compose up --build
```

### 4. Verify Setup
Visit [http://localhost:8000/docs](http://localhost:8000/docs) to check API documentation.

---
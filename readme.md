

````markdown
# E-commerce Store API

This is the backend API for an e-commerce store built using **FastAPI**, **SQLAlchemy**, and **PostgreSQL**. The project includes features like product management, user authentication, order handling, and payment processing, among others.

## Features

- **User Authentication**: Register, login, and role-based access control (admin, user, seller).
- **Product Management**: CRUD operations for products, categories, and stock management.
- **Order Management**: Place and manage orders, including invoice generation and tracking.
- **Cart System**: Manage user shopping carts and checkout process.
- **Payment Integration**: Stripe and PayPal for payment processing.
- **Email Notifications**: Send order confirmation and invoice emails.
- **Admin Dashboard**: View and manage users, orders, products, and reports.
  
## Technologies

- **FastAPI** for building the web API.
- **SQLAlchemy** for ORM-based database interaction.
- **PostgreSQL** as the relational database.
- **Alembic** for database migrations.
- **Stripe** and **PayPal** for payment processing.
- **Pydantic** for data validation.

## Requirements

- Python 3.9+
- PostgreSQL
- Alembic (for database migrations)
- Stripe API keys
- SendGrid or SMTP for email notifications

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/parthkajavadra/ecommerce-store.git
cd ecommerce-store
````

### 2. Create a Virtual Environment

Create a Python virtual environment using `venv`:

```bash
python3 -m venv env
```

Activate the environment:

* For macOS/Linux:

```bash
source env/bin/activate
```

* For Windows:

```bash
.\env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL

Ensure you have PostgreSQL installed and running. Create a database and user:

```sql
CREATE DATABASE ecommerce_db;
CREATE USER ecommerce_user WITH PASSWORD 'yourpassword';
ALTER ROLE ecommerce_user SET client_encoding TO 'utf8';
ALTER ROLE ecommerce_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ecommerce_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory and add your environment variables:

```env
DATABASE_URL=postgresql://ecommerce_user:yourpassword@localhost/ecommerce_db
SECRET_KEY=your_secret_key
STRIPE_SECRET_KEY=your_stripe_secret_key
SENDGRID_API_KEY=your_sendgrid_api_key
```

### 6. Run Database Migrations

```bash
alembic upgrade head
```

This will apply the latest database schema changes.

### 7. Start the Application

```bash
uvicorn app.main:app --reload
```

The API will be accessible at `http://127.0.0.1:8000`.

### 8. Test the API

You can test the API by navigating to `http://127.0.0.1:8000/docs` in your browser. FastAPI automatically generates interactive documentation using Swagger UI.

## Available Endpoints

* **POST** `/users/register`: Register a new user.
* **POST** `/users/login`: Login to get an authentication token.
* **GET** `/products`: Get a list of products.
* **POST** `/orders`: Create a new order.
* **POST** `/orders/{order_id}/generate_invoice`: Generate an invoice for an order.

## Running Tests

To run tests for the application, you can use:

```bash
pytest
```

This will run all the tests defined in the `tests` directory.

## Deployment

For deployment, you can use services like **Docker**, **Heroku**, or **AWS**. You will need to configure environment variables (e.g., `DATABASE_URL`, `SECRET_KEY`, etc.) according to your chosen platform.

### Docker Deployment

1. Build the Docker image:

```bash
docker build -t ecommerce-store .
```

2. Run the Docker container:

```bash
docker run -d -p 8000:8000 ecommerce-store
```
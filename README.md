# Text-to-handwriting
# Text to Handwriting Generator (Django + Celery + Redis)

## Introduction
This is a Django-based web application with an API that converts text into handwritten-style output. The project supports asynchronous task processing using Celery and Redis, ensuring efficient handling of API requests.

## Features
- Text-to-handwriting conversion  
- REST API for generating handwriting from text  
- Django framework for web development  
- Celery for background task processing  
- Redis as message broker for Celery  
- API authentication 
- Asynchronous processing for improved performance  

## Installation

### Prerequisites
Ensure you have the following installed:  
- Python (>=3.8)  
- PostgreSQL or SQLite  
- Redis  
- Virtualenv (optional but recommended)  

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Qobi1/Text-to-handwriting.git
   cd text_to_handwriting
   ```
   
2. **Create a virtual environment and activate it:**   
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables:**
Create a .env file in the root directory and add necessary configurations (example below):
    ```
    SECRET_KEY=your_secret_key
    DEBUG=True
    DATABASE_URL=postgres://user:password@localhost:5432/dbname
    CELERY_BROKER_URL=redis://localhost:6379/0
    ```
   
5. **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

6. **Create a superuser (if needed):**
    ```bash
    python manage.py createsuperuser
    ```

7. **Start Redis Server:**
    ```bash
    redis-server
    ```
8. **Start Celery Worker:**
    ```bash
   celery -A text_to_handwritting worker --loglevel=info
    ```

9. **Run the Django server:**
    ```bash
    python manage.py runserver
    ```

# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8000 for Django
EXPOSE 8000

# Correct way to run the Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

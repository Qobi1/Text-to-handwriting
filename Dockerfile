FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /text_to_handwrwiting

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

EXPOSE 8000
CMD ["gunicorn", "--workers=4", "--threads=4", "--bind=0.0.0.0:8000", "text_to_handwritting.wsgi"]


FROM python:3.12-slim

WORKDIR /app


RUN apt-get update && \
    apt-get install -y \
    gcc \
    libpq-dev \
    unixodbc \
    odbc-postgresql && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
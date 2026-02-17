FROM python:3.11-slim

# Install system dependencies for pycairo
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "lms_project.wsgi:application"]

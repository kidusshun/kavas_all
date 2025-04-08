# Use official Python image as base
FROM python:3.11-slim


WORKDIR /app


COPY main-requirements.txt main-requirements.txt

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    build-essential \
    libglib2.0-0 \
    g++ \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r main-requirements.txt
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
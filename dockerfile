FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .
ENV HTTP_PROXY=http://10.128.0.4:3128
ENV HTTPS_PROXY=http://10.128.0.4:3128
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["python", "main.py"]
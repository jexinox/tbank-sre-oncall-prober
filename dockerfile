FROM python:3.9-slim

WORKDIR /app

COPY . .
ENV HTTP_PROXY=http://10.128.0.4:3128
ENV HTTPS_PROXY=http://10.128.0.4:3128
ENV NO_PROXY=".local"
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["python", "main.py"]
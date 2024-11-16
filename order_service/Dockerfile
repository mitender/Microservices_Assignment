# order_service/Dockerfile
FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip install fastapi pymongo pika uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]

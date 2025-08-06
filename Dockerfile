FROM python:3.11.8-slim-bookworm

WORKDIR /app

RUN pip install --no-cache --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache -r requirements.txt

COPY . .

EXPOSE 8080

ENTRYPOINT ["python", "./server.py"]
# , "--host", "0.0.0.0", "--port", "8080"]
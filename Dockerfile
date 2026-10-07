FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
# Se o contrato pedir frontend, descomente — esquecer isto dá 404 só no container:
# COPY public/ ./public/

EXPOSE 8080
CMD ["python3", "src/app.py"]

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src-pcs/ ./src_pcs

COPY infra/json/leaked_passwords.json ./leaked_passwords.json

EXPOSE 8000

CMD ["uvicorn", "src_pcs.app:app", "--host", "0.0.0.0", "--port", "8000"]

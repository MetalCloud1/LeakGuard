FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src_pcs/ ./src_pcs

EXPOSE 8000

CMD ["uvicorn", "src_pcs.app:app", "--host", "0.0.0.0", "--port", "8000"]

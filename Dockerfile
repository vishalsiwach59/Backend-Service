FROM python:3.9-slim

WORKDIR /
COPY . .

RUN pip install --no-cache-dir -r backendservice/requirements.txt

CMD ["uvicorn", "backendservice.main:app", "--host", "0.0.0.0", "--port", "8000"]

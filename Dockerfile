FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_trf

COPY . /app/

EXPOSE 80

# Run uvicorn
CMD ["uvicorn", "backend.asgi:application", "--host", "0.0.0.0", "--port", "80"]

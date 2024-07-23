# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Expose the port that uvicorn will run on
EXPOSE 8000

# Run uvicorn
CMD ["uvicorn", "backend.asgi:application", "--host", "127.0.0.1", "--port", "8000"]

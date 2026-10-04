FROM python:3.11-slim

# Prevent python from writing pyc files and keep stdout unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy project definition
COPY pyproject.toml /app/

# Install the project dependencies
RUN pip install --no-cache-dir .

# Copy the rest of the application
COPY . /app/

EXPOSE 8000

# Start the application
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

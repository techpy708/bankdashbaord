# Use official Python base image
FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Use HTTPS for apt sources (optional)
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list

# Install system dependencies (minimal, no PostgreSQL or MySQL needed for SQLite)
# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc build-essential \
    && rm -rf /var/lib/apt/lists/*


# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your entire Django project
COPY . .

# Expose port for Gunicorn
EXPOSE 8000

# Entry point without PostgreSQL wait
ENTRYPOINT ["/bin/sh", "-c", "\
  echo 'Running migrations...'; \
  python manage.py migrate && \
  python manage.py collectstatic --noinput && \
  python manage.py load_help_docs && \
  echo 'Starting Gunicorn...'; \
  exec gunicorn docmanager.wsgi:application --bind 0.0.0.0:8000 \
"]

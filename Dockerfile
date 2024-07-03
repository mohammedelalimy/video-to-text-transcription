# Use a slim Python image as the base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy application files into the container
COPY . /app

# Create and set permissions for the uploads and cache directories
RUN mkdir -p /app/uploads /app/.cache && chmod 777 /app/uploads /app/.cache

# Set environment variable for the cache directory
ENV XDG_CACHE_HOME=/app/.cache

# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 7860

# Define the entrypoint for the container with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:7860", "-w", "4", "-k", "gevent", "--timeout", "300", "app:app"]

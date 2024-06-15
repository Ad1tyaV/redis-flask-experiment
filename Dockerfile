# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install SQLite3 and Redis server
RUN apt-get update && apt-get install -y \
    sqlite3 \
    redis-server && \
    rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for the Flask app
EXPOSE 5000

# Copy and run the Redis configuration file
COPY redis.conf /usr/local/etc/redis/redis.conf

# Start the Redis server and the Flask application
CMD redis-server /usr/local/etc/redis/redis.conf & python app.py

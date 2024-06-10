# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set noninteractive mode for apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for Pygame
RUN apt-get update && apt-get install -y \
    # Necessary tools
    python3-pygame \
    # X11 for graphics output
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any additional dependencies specified in requirements.txt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables to configure Python buffering
ENV PYTHONUNBUFFERED=1

# Define environment variable to improve print output logging
ENV PYTHONUNBUFFERED=1

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["python3", "main.py"]

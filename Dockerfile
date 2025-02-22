# Base image
FROM python:3.8.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies
RUN python3 -m pip install --upgrade pip && pip3 install -r ./requirements.txt

# Copy the app code into the container
COPY . .

# Expose api on port 8000
EXPOSE 8000
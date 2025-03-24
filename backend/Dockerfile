# Use the official Python image from the Docker Hub
FROM python:3.12.8-alpine3.21

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set the environment variable
ENV DOCKER=true

# Expose the port the application runs on
EXPOSE 8000

# Specify the command to run the application
CMD ["fastapi", "run", "main.py"]
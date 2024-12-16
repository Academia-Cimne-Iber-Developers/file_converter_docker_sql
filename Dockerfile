# Use the official Python image from the Docker Hub with version 3.12
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Expose port 5000 for the Flask app
EXPOSE 5050

# Run the Uvicorn server
CMD ["uvicorn", "asgi:asgi_app", "--host", "0.0.0.0", "--port", "5050", "--workers", "4"]
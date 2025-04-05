# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Change working directory to /app/src
WORKDIR /app/src

# Expose the FastAPI port
EXPOSE 8002

# Define the command to run the application
CMD ["uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "8002"]

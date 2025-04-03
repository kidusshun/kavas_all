# Use an official Python runtime as a parent image
FROM python:3.12.5-bullseye
# Set the working directory in the container
WORKDIR /app
# copy requirements.txt to the container
COPY /requirements.txt .

# Install Streamlit and any other needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Copy the current directory contents into the container at /app
COPY . .

EXPOSE 8001
# Define the command to run the uvicorn server
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8001"]
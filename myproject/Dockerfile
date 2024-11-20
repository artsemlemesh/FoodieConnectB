# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app



# Copy the requirements file into the container
COPY requirements.txt .


# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*


# Copy the entire project into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
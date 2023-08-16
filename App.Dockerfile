# Use the official Python image as the base image
FROM python:3.8-slim-buster

# Set the working directory
WORKDIR /app

# Install dependencies
RUN pip install cryptography sqlalchemy==2.0.19 pymysql==1.1.0 openai==0.27.8 llama-index==0.8.1.post1 nltk==3.8.1 flask==2.3.2

# Copy the rest of the application files
COPY . .

# Expose port 5000
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
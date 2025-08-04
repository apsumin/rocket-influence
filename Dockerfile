# Dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED True

# Create app directory
WORKDIR /app

# Copy application code
COPY . /app/


# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (This is mostly for documentation; Cloud Run uses $PORT)
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]
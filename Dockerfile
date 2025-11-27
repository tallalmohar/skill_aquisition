# Start with Python 3.11
FROM python:3.11-slim

# Set up the folder
WORKDIR /app

# Install libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . .

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# 1. Use official Python base image
FROM python:3.11-slim

# 2. Set working directory inside the container
WORKDIR /app

# 3. Copy dependencies file first (for caching)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy your app code
COPY . .

# 6. Expose port FastAPI will run on
EXPOSE 8000

# 7. Command to start the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

## docker build -t my-fastapi-app .
## docker run -d -p 8000:8000 my-fastapi-app



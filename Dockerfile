# Stage 1: Install dependencies
FROM python:3.12 AS builder

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

# Stage 2: Copy only necessary files to final container
FROM python:3.12 AS final

WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy application source code
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Command to run FastAPI
CMD ["uvicorn", "app.service.main:app", "--host", "0.0.0.0", "--port", "8000"]



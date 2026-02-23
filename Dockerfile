FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Ensure Python can find your src package
ENV PYTHONPATH=/app/src

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose container port
EXPOSE 8000

WORKDIR /app/src/app
CMD ["uvicorn", "wallet.main:app", "--host", "0.0.0.0", "--port", "8000"]
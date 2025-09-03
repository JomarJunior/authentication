FROM python:3.10-slim

# Install Poetry
RUN pip install poetry

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install --without dev --no-interaction --no-ansi

# Expose port (optional, adjust as needed)
EXPOSE 8080

# Set default command (adjust as needed)
CMD ["python", "main.py"]
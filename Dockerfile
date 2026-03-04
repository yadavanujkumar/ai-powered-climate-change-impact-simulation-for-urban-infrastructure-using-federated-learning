FROM python:3.11-slim AS builder

# Metadata as described above
LABEL maintainer="your_email@example.com" \
      version="1.0" \
      description="AI-Powered Climate Change Impact Simulation for Urban Infrastructure Using Federated Learning"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

# Create a non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Set the working directory
WORKDIR $APP_HOME

# Install system dependencies and Python packages
COPY requirements.txt ./
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
        libssl-dev \
        && pip install --no-cache-dir -r requirements.txt \
        && apt-get purge -y --auto-remove gcc libffi-dev libssl-dev \
        && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Stage 2: Runtime image
FROM python:3.11-slim AS runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

# Create a non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Set the working directory
WORKDIR $APP_HOME

# Copy only the necessary files from the builder stage
COPY --from=builder $APP_HOME /app

# Set permissions for the application files
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Health check directive
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application
ENTRYPOINT ["python", "app.py"]

# Expose the application port
EXPOSE 8000

# Document environment variables
ENV APP_ENV=production \
    APP_PORT=8000

# Note: If GPU support is needed, additional CUDA dependencies should be added in the builder stage.
# This can be done by using a base image that supports CUDA and installing the necessary libraries.
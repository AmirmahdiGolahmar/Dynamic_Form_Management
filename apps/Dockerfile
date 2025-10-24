# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /apps

# Prevents .psy files + ensures logs output immediately
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# Install system dependencies
RUN apt-get update && apt-get install -y netcat-traditional && apt-get clean

# Install Python depencencies
COPY ../requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt 


# Copy project files
COPY . .


# Entrypoint script
ENTRYPOINT [ "/apps/entrypoint.sh" ]
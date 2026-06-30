# Dockerfile for muvistat

# Base Linux image with Python (keep it small)
FROM python:3.13-slim

# Working directory for the app within the container
WORKDIR /code

# Dependencies (cached if requirements.txt is unchanged)
COPY ./requirements.txt /code/requirements.txt
# Do not use cache to save space:
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Code (after dependecies -> Docker layer caching)
COPY ./app /code/app

# Port to listen for incoming network traffic on
EXPOSE 8000

# Default command to run the application
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]

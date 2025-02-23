FROM python:3.9-slim
# Set the working directory in the container
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
# Install any needed dependencies specified in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Make port 5000 available to the world outside this container
EXPOSE 8080
# Define environment variable
ENV FLASK_APP=app.py
# Run app.py when the container launches
CMD ["python", "app.py"]
# CMD ["flask", "run"]
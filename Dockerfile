# 🔥 Use the full Python image (includes SQLite3 by default)
FROM python:3.13

# 🔥 Set the working directory
WORKDIR /app

# 🔥 Copy project files
COPY . /app

# 🔥 Install Python dependencies
RUN pip install --no-cache-dir flask flask-cors requests

# 🔥 Expose Flask port
EXPOSE 5000

# 🔥 Run the server
CMD ["python", "server.py"]

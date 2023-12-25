FROM python:3.10

# Set working directory
WORKDIR /app

# Copy requirements.txt and install
COPY ./Flask/requirements.txt /app/
RUN pip install -r requirements.txt

# Copy Scrapy project
COPY ./Flask /app

# Expose port 8080
EXPOSE 8080

# Set vars
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run Flask App
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
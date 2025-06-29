FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Train the model
RUN rasa train

EXPOSE 5005

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:5005 || exit 1

CMD ["rasa", "run", "--enable-api", "--cors", "*", "--port", "5005", "--debug"]
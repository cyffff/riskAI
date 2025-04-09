FROM python:3.7.6-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy actions code
COPY . /app/actions/

# Set environment variables
ENV PYTHONPATH=/app

EXPOSE 5055

CMD ["rasa", "run", "actions", "--debug"] 
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY assets/ assets/
COPY tests/ tests/
COPY templates/ templates/
COPY static/ static/
COPY .env.example .

EXPOSE 8080
CMD ["python", "-m", "src.app"]

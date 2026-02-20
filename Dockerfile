# baseimage
FROM Python:3.11-slim

# working directory in the container
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copy application code

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
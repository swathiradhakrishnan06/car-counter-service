FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN pip install python-multipart

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
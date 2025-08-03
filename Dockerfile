FROM python:3.9-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /
WORKDIR $APP_HOME
COPY . /


ENV PORT 8080

RUN pip install --no-cache-dir -r requirements.txt


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]

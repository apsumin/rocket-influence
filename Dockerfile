FROM python:3.9-slim

ENV PYTHONUNBUFFERED True
ENV PORT 8080


COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . $APP_HOME/.





CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]

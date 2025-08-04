FROM python:3.9-slim

ENV PYTHONUNBUFFERED True
ENV PORT 8080
ENV APP_HOME /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . $APP_HOME/.
WORKDIR $APP_HOME

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]

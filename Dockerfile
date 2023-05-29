FROM python:3.11.0-slim-bullseye

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir

COPY . .

CMD ["gunicorn", "main:APP", "-c", "gunicorn.py"]
FROM python:3.10-alpine

RUN apk add py3-pip

WORKDIR /var/www/ispportal

COPY ispportal /var/www/ispportal

RUN pip install -r /var/www/ispportal/requirements.txt

EXPOSE 5028

CMD ["python3", "run.py"]
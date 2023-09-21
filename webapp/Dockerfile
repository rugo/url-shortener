FROM python:3

WORKDIR /usr/src/app

ADD requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
RUN useradd -U gunicorn

ADD . ./

CMD gunicorn -b 0.0.0.0:8888 -u gunicorn -g gunicorn wsgi:app
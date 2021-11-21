FROM python:3.8-slim-buster

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev 

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org --no-cache-dir -r requirements.txt
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org --no-cache-dir gunicorn

COPY . /app

ENV FLASK_APP=main.py

WORKDIR /app/SecureGenericForum

CMD [ "gunicorn", "-b" ,"0.0.0.0:5000", "main:app"]
# CMD [ "uwsgi", "--ini", "uwsgi.ini" ]
# CMD [ "python3", "main.py" ]

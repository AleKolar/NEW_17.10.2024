# FROM python:3.9
#
# ENV PYTHONUNBUFFERED=1
#
# WORKDIR /code
#
# COPY ./app11/requirements.txt /code/
# RUN pip install -r requirements.txt
#
# COPY . /code/
#
# RUN pip install python-dotenv
# RUN pip install psycopg2-binary
#
# ENV STATIC_ROOT=/code/staticfiles
#
# RUN python manage.py collectstatic --noinput
#
# EXPOSE 8000
#
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM python:3.9

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY ./requirements.txt /code/

RUN pip install -r /code/requirements.txt

COPY . /code/

RUN pip install psycopg2-binary

ENV STATIC_ROOT=/code/staticfiles

RUN pip install "python-dotenv[cli]"

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
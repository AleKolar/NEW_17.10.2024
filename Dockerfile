FROM python:3.9

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY ./prjt/app11/requirements.txt /code/

RUN pip install -r requirements.txt

COPY ./prjt /code/

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
web: gunicorn core.wsgi --log-file -
worker: celery -A core worker -c 10 -B --loglevel=info

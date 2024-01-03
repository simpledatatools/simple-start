SimpleStart

celery -A core worker -l info
celery -A core beat -l info

Heroku Redis Flag
?ssl_cert_reqs=CERT_NONE
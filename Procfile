web: python djangoweatherreminder/manage.py runserver 0.0.0.0:$PORT
worker: celery -A djangoweatherreminder worker -l info --pool=solo  --without-heartbeat --without-gossip --without-mingle
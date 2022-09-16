web: python djangoweatherreminder/manage.py runserver 0.0.0.0:$PORT
main_worker: celery -A djangoweatherreminder worker --beat -events -l info --pool=solo  --without-heartbeat --without-gossip --without-mingle

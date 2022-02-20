docker exec -ti real_state_backend python3 manage.py collectstatic --noinput && \
docker-compose exec backend python3 manage.py migrate
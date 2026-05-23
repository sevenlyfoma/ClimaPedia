cd /workspace
source .env
# source /workspace/.venv/bin/activate

cd /workspace/backend

nohup poetry run python -m group52.data_uploading.start_uploading_daemon PROD &
echo "Starting gunicorn on port=$BACKEND_PORT"
poetry run gunicorn --bind 0.0.0.0:$BACKEND_PORT wsgi:app
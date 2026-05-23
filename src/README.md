# ClimaPedia - 3099 SG5


## Docker
This project uses [Docker](https://www.docker.com/) for containerization and environment management.

## Running the Application
The `.env` file does not need `export` in front of variables.

### .env file for the database
You need the following entries in the `.env` file for the database. `DB_HOST` and `MYSQL_DATABASE` must contain those values. All other values should be set as required.
```sh
DB_HOST=db
MYSQL_DATABASE=weather
MYSQL_ROOT_PASSWORD=...
MYSQL_USER=...
MYSQL_PASSWORD=...
```

### If you want the database to load without waiting forever (not for final prod)
Rename `db/migrations/01predictions.py` to `db/migrations/01predictions.py.temp`:
```sh
$ mv db/migrations/01predictions.py db/migrations/01predictions.py.temp
```

This will disable the predictions migration which takes forever (it's training an ML model).


### To run the application in production mode
1. In your `.env` file:
    1. Change `FLASK_ENV` in  to `production`
    2. Change `FRONTEND_API_PATH` to `"/api/"`
    3. Remove `DB_PORT` env variable
2. Run:

        bash run.sh

This will:
1. Stop the existing Docker container instance, if it is running
2. Load the environment variables from `.env` into the new container
3. Update dependencies in `frontend` and `backend`
4. Build the frontend application to `frontend/dist` as static files
5. Run the Flask server, which also serves the static files generated in step 4

Feel free to add new applications to the instance in `entrypoint.sh`, but bear a few things in mind:
1. Any continuously running process must be turned into a subprocess by adding `&` to the end of the command, so that the whole script can continue executing
2. If the application has an outward-facing port, it must be exposed (see `run.sh:6-7`)

### To run the application in developer mode, you must run the backend and frontend separately
1. In your `.env` file:
    1. Change `FLASK_ENV` in  to `development`
    2. Change `FRONTEND_API_PATH` to `"localhost:<BACKEND_PORT>/api/"` (replace \<BACKEND_PORT\> with the actual value)
    3. Set `DB_PORT` to `3307`
2. In one shell process:
    ```
    python3 -m install -U pipx
    pipx install poetry
    pipx ensurepath
    poetry install
    cd backend
    poetry run python app.py
    ```

4. In another process:
    ```
    cd frontend
    npm install
    npm run dev
    ```
4. In a third process start the database:
    ```sh
    podman-compose -f docker-compose.development.yml up --build
    ```
5. After starting the database, it should populate it with group52 data (this may not be visible and may take some time), but if this does not occur, then can be done using:
    ```sh
    cd backend
    poetry run python -m group52.data_uploading.start_uploading_daemon PROD
    ```
    > This will also cause the database to update with any new values daily at 1AM.

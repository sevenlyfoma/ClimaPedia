# Weather Project Backend


## Backend Virtual Environment and Dependencies

After cloning the project for the first time, make sure to set up the virtual environment within the `backend/` directory. This can be done by simply running the app once with Docker; see the steps in the README at the project root directory.

### Activating the Virtual Environment
When developing in the backend, first make sure the virtual environment is active. Run the following command:

    . .venv/bin/activate

You must have this shell process active before doing anything which affects or uses project dependencies, such as:
- Running the backend application on its own
- Importing Python modules with `pip install`
- Saving dependencies for for export to the repository (see below)

### Saving Dependencies
After installing new dependencies to the venv, you can save them by running the following command from within `backend/`:

    pip freeze > requirements.txt


## Running the Backend Application

If you want to run the backend application separately from the entire application, you can do so by following these steps:

```
. .venv/bin/activate
pip install -r requirements.txt
. ../.env
python3 app.py
```

If the Docker instance is already running, you will need to stop it before running the backend application on its own:

    docker kill weather-app

The API endpoint will now be accessible at `localhost:$BACKEND_PORT`, where `$BACKEND_PORT` is the port specified in the `.env` file in root.

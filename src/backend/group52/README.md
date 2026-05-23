# Group 52

## db_accessor setup (Station and Historical Weather data database accessor)

<!-- - **To run the database a .env file is required in the group52 directory** -->

- Copy and input this data into the .env file to connect to the DB:
```sh
DB_HOST=localhost
DB_PORT=3307
MYSQL_USER="cs3099usersg5"
MYSQL_PASSWORD="w.8Nj32jKnTb26"
```

- Run the backend DB with `podman-compose -f docker-compose.development.yml up --build -d

- We are aware it is bad practice to have access information in the repo. (added due to ease of access)

## Data retrieval

First, install all requirements:
```bash
# For info on installing poetry see project README.
project-code $ poetry install
project-code $ poetry shell  # Activate the environment.
```

The data can be gotten from wikidata by running:
```bash
(poetry-env) .../group52/data_retrieval $ python3 get_histories.py <outfile name>
```

This will, by default, fetch data about all weather stations with history. To get the weather history for all stations as well, pass in the `--history` flag:
```bash
(poetry-env) .../group52/data_retrieval $ python3 get_histories.py <outfile> --history
```

## Data sanitisation
First get the necessary python packages (see installation in [Data Retrieval](#data-retrieval))

The currently used cleaning files are
    clean_data_formatting.py (relying on cleaning_functions.py)
    reorder_columns.py
    prepare_csv.py

clean_data_formatting
    this is run in the command line like this:
    python clean_data_formatting.py [mapping_file_json] [target_json_file] [destination_json_file]
    the mapping file is in the following format
        {
        "fieldname1":{"cleaningFuncs":["cleaning_function_1", "cleaning_fuinction_2"], "cleaningArgs":[["value"],[]]},
        "fieldname2":{"cleaningFuncs":[], "cleaningArgs":[]},
        ...
        }
        each filed is specified a list of strings of names of cleaning functions, specified in cleaning_functions.py
        for each function, cleaning args should have another corresponding list within it, carrying the arguments for each specified function
    This is run as many times you need based on the number of mapping stages

    Generally it has been run like this in /project_code, ADAPT THIS IF YOU ARE NOT RUNNING IT THERE:
        python data_sanitisation/clean_data_formatting.py data_sanitisation/utility/1.non_history_refinement_mappings.json non_history_data/1.non_history_data.json non_history_data/2.extracted_non_history_data.json
        python data_sanitisation/clean_data_formatting.py data_sanitisation/utility/2.extracted_mappings.json non_history_data/2.extracted_non_history_data.json  non_history_data/3.cleaned_non_history_data.json
        python data_sanitisation/clean_data_formatting.py data_sanitisation/utility/3.type_conversion_mappings.json non_history_data/3.cleaned_non_history_data.json  non_history_data/4.final_non_history_data.json

reorder_columns
    this is run in the command line like this:
    python data_sanitisation/reorder_columns.py [reordering_txt_file] [target_json_file] [destination_json_file]
    the reordering file is in the following format
        field1,field2,field3,field4
    the target json files columns will be reordered in the above order
    every field specified must correspond to a field in the json

    Generally it has been run like this in /project_code, ADAPT THIS IF YOU ARE NOT RUNNING IT THERE:
        python data_sanitisation/reorder_columns.py data_sanitisation/utility/4.reordering.txt non_history_data/4.final_non_history_data.json non_history_data/5.reordered_final_non_history_data


prepare_csv
    this is run in the command line like this:
    python data_sanitisation/prepare_csv.py [target_json_file] [destination_csv_file]
    The json will be stored as a csv in the destination

    Generally it has been run like this in /project_code, ADAPT THIS IF YOU ARE NOT RUNNING IT THERE:
        python data_sanitisation/lib/prepare_csv.py non_history_data/5.reordered_final_non_history_data non_history_data/6.non_history_data_csv.csv

To run tests
    python -m unittest discover

## Keeping data updated
To get the data and sanitise it, and make it continue to do so periodically (every night at 1AM), you should install all requirements (See installation in [Data Retrieval](#data-retrieval)) and run [`run_data.py`](./run_data.py). This should be done in headless mode, so that the script can keep running when the terminal is closed:
```bash
nohup python3 run_data.py &
```

To stop the script in headless mode, the following steps should be followed:
```bash
ps -ef | grep python3 # to get pid
```
> The recommended way to get the pid is to pipe this output to a file, and search the file for your username.
    i.e. use something like `ps -ef | grep python > out.txt`
> This will give all processes of your user, and so the headless process can then be found easily
Then, simply run `kill <pid>` to kill the process.

"""
Group 51 - db/migrations/01predictions.py


"""

from numpy.typing import NDArray
from pymysql.cursors import Cursor

import os
import os.path
import tempfile
import shutil
import itertools
import re
import time
import json

from datetime import datetime, timedelta

import requests
import numpy as np
import pandas as pd

from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error

SCHEMA = """
DROP TABLE IF EXISTS `prediction`;
CREATE TABLE `prediction`(
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `station_id` CHAR(20),
    `datetime` DATETIME,
    `temperature` DOUBLE,
    `is_prediction` BOOLEAN,
    UNIQUE (`station_id`, `datetime`, `is_prediction`)
);
"""

URL_PREFIX = "https://dd.weather.gc.ca/climate/observations/hourly/csv/{}/{}"
CANADIAN_REGIONS = [
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "ON",
    "PE",
    "QC",
    "SK",
    "NT",
    "NU",
    "YT",
]
HOURS_BACK = 5

RAW_DATA_PATH = "/rawdata"
RESULTS_DIR = "/results"

LABEL_COLS = ["Temp (C)"]

META_COLS = ["Longitude (x)", "Latitude (y)", "Climate ID", "Date/Time (LST)"]

STATIC_COLS = META_COLS + [
    "Day in Year",
    "Time in Day",
]

FORMATTED_COLS = (
    STATIC_COLS
    + list(
        itertools.chain.from_iterable(
            [f"{s}-{i}" for s in LABEL_COLS] for i in range(HOURS_BACK)
        )
    )
    + LABEL_COLS
)

# STATIONS = [
#     "6010735",
#     "6014351",
#     "6014353",
#     "6016295",
#     "6016298",
#     "6016525",
#     "6016528",
#     "6016970",
# ]

TRAIN_YEARS = ["2014", "2015"]
ACTUAL_YEARS = ["2016"]


# region get_hourly_data
def get_hourly_data(region: str, data_path: str, stations: list[str], years: list[str]):

    # Extract requested stations by year and ID.
    name_fmt = "climate_hourly_{}_{}_{}_P1H.csv"

    # Write csv files to '/data_raw'.
    for station in stations:
        for year in years:
            name = name_fmt.format(region, station, year)
            fpath = os.path.join(data_path, name)

            if not os.path.exists(fpath):
                url_path = URL_PREFIX.format(region, name)
                r = requests.get(url_path)
                print(f"Got path {url_path}", flush=True)
                if r.status_code == 200:
                    with open(fpath, "wb") as f:
                        f.write(r.content)
                else:
                    print(
                        f"Error getting {url_path}, got code {r.status_code}",
                        flush=True,
                    )
            else:
                print(f"Have {fpath}, skipping", flush=True)


def make_hourly_dateframe(f_path: str):
    # Create new dataframe with relevant columns.
    core = pd.read_csv(f_path, encoding="ISO-8859-1")

    # Cleaning and sorting of relevant columns.
    core.sort_values(["Date/Time (LST)"], inplace=True)

    # Use 'Data/Time' column to calculate 'Day in Year' metric.
    core["Day in Year"] = pd.to_datetime(core["Date/Time (LST)"]).dt.day_of_year / 366

    # Do this one with a rename.
    core["Time (LST)"] = pd.to_datetime(core["Time (LST)"], format="%H:%M").dt.hour / 24
    core.rename(
        columns={
            "Temp (°C)": "Temp (C)",
            "Time (LST)": "Time in Day",
            "Dew Point Temp (°C)": "Dew Point Temp (C)",
        },
        inplace=True,
    )
    return core.dropna(subset=LABEL_COLS)


def format_hourly_csv(df: pd.DataFrame, out_path: str):
    """Format to make hourly predictions

    Parameters:
        df: The DataFrame of features to format.
        out_path: The path to save the result at.
    """
    # Create columns for 'Day in Year' metrics required for training.
    out_arr = []

    narr = df[STATIC_COLS + LABEL_COLS].to_numpy()
    lab_start = len(STATIC_COLS)
    lab_end = lab_start + len(LABEL_COLS)

    flat = narr[:, lab_start:lab_end].flatten()

    for i in range(df.shape[0] - HOURS_BACK):
        out_arr.append(
            np.concatenate(
                (
                    narr[i, : len(STATIC_COLS)],
                    flat[i * len(LABEL_COLS) : (i + HOURS_BACK) * len(LABEL_COLS)],
                    narr[i + HOURS_BACK, lab_start:lab_end],
                )
            )
        )

    print(f"Saved formatted at {out_path}", flush=True)

    pd.DataFrame(out_arr, columns=FORMATTED_COLS).to_csv(out_path, index=False)


def run_hourly_data_processing(training_path: str, years: list[str]) -> pd.DataFrame:
    """Get the data from a list of station IDs and years. Populated training_path.

    Parameters:
        training_path: The path to output the training data to. Must be a directory.
        stations: A list of stations to get.
        years: A list of years to get.

    Raises:
        ValueError: If training_path is not a directory.
    """
    if not os.path.isdir(training_path):
        raise ValueError("training_path must be a directory. (given value was not)")

    # Define RegEx for HTTP request.
    base_pattern = r"climate_hourly_{}_(\d+)_{}_P1H\.csv"
    # Format with nothing to get all.
    print("Getting station list", flush=True)

    stations = set()
    for region in CANADIAN_REGIONS:
        response = requests.get(URL_PREFIX.format(region, ""))
        content = response.text
        reg_stations = set()
        for year in years:
            # Format pattern to include specified year(s) and obtain station list.
            pattern = base_pattern.format(region, year)
            reg_stations = reg_stations.union(
                set(dict.fromkeys(re.findall(pattern, content)))
            )
        get_hourly_data(region, RAW_DATA_PATH, reg_stations, years)
        stations = stations.union(reg_stations)
    # stations = set(STATIONS)
    # get_hourly_data("ON", RAW_DATA_PATH, stations, years)

    # Inplace format of files in '/data_raw'.
    F_RE = r"climate_hourly_[A-Z]{2}_(\d+)_(\d{4})_P1H.csv"

    for d in os.listdir(RAW_DATA_PATH):
        read_file = True
        if (matches := re.match(F_RE, d)) is not None:
            station = matches.group(1)
            year = matches.group(2)
            if year not in years or station not in stations:
                read_file = False
        else:
            read_file = False

        if read_file:
            df = make_hourly_dateframe(os.path.join(RAW_DATA_PATH, d))
            format_hourly_csv(df, os.path.join(training_path, d))


# endregion


def feat_label_split(
    dir: str, meta_cols: list[str], label_cols: list[str]
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Get the features and labels from a data set by directory.

    Parameters:
        dir: The data set directory.
        label_cols: The columns to use as labels in training.

    Returns:
        pd.DataFrame: (n_instances, r_meta) array of meta information about each instance.
        pd.DataFrame: (n_instances, m_features) array of features.
        pd.DataFrame: (n_instances, p_responses) array of labels.
    """

    feats = (
        pd.concat([pd.read_csv(os.path.join(dir, d)) for d in os.listdir(dir)])
        .reset_index(drop=True)
        .dropna(subset=LABEL_COLS)
    )

    labels = pd.concat([feats.pop(c) for c in label_cols], axis=1).reset_index(
        drop=True
    )

    meta = pd.concat([feats.pop(c) for c in meta_cols], axis=1).reset_index(drop=True)

    return (meta, feats, labels)


def create_train_model(feats: NDArray, labels: NDArray) -> Pipeline:
    """Create and train a model on features and labels.

    Parameters:
        feats: (n_instances, m_features) array of features.
        labels: (n_instances, p_responses) array of labels.

    Returns:
        A trained model.
    """

    model = make_pipeline(
        StandardScaler(),
        MLPRegressor(
            hidden_layer_sizes=(30, 30, 30),
            solver="lbfgs",
            activation="relu",
            learning_rate_init=0.00016622095016505746,
            max_iter=1000,
        ),
    )

    model.fit(feats, labels)

    return model


def get_baseline_predictions(feats: pd.DataFrame) -> NDArray:
    """Get the baseline predictions for the feature set.

    Parameters:
        feats: DataFrame of features.

    Returns:
        An array of results.
    """
    return feats[[f"Temp (C)-{i}" for i in range(HOURS_BACK)]].mean(axis=1).to_numpy()


def make_migration(conn, cur: Cursor) -> None:
    """Make migrations for predictions."""
    mig_start_time = time.time()
    cur.execute(SCHEMA)

    train_dir = tempfile.mkdtemp()
    actual_dir = tempfile.mkdtemp()

    # Get hourly training data.
    run_hourly_data_processing(train_dir, TRAIN_YEARS)
    # Don't need the meta information about the training data.
    _, train_feats, train_labels = feat_label_split(train_dir, META_COLS, LABEL_COLS)
    # Get actual data.
    run_hourly_data_processing(actual_dir, ACTUAL_YEARS)
    actual_meta, actual_feats, actual_labels = feat_label_split(
        actual_dir, META_COLS, LABEL_COLS
    )

    # Train model.
    print("Training model...", flush=True)
    train_start_time = time.time()
    model = create_train_model(np.array(train_feats), np.array(train_labels))
    train_time = time.time() - train_start_time

    # Make predictions.
    print("Making predictions...", flush=True)
    actual_preds = pd.DataFrame(
        model.predict(np.array(actual_feats)), columns=LABEL_COLS
    )

    baseline_preds = get_baseline_predictions(actual_feats)

    model_mae = mean_absolute_error(actual_labels.to_numpy(), actual_preds.to_numpy())
    model_baseline_mae = mean_absolute_error(actual_labels.to_numpy(), baseline_preds)

    # Store in database.
    preds_table = pd.concat([actual_meta, actual_preds], axis=1)
    cur.executemany(
        "INSERT INTO `prediction`(`station_id`, `datetime`, `temperature`, `is_prediction`) VALUES(%s, %s, %s, TRUE)",
        preds_table.astype(dtype="string").values.tolist(),
    )

    actuals_table = pd.concat([actual_meta, actual_labels], axis=1)
    cur.executemany(
        "INSERT INTO `prediction`(`station_id`, `datetime`, `temperature`, `is_prediction`) VALUES(%s, %s, %s, FALSE)",
        actuals_table.astype(dtype="string").values.tolist(),
    )

    shutil.rmtree(train_dir)
    shutil.rmtree(actual_dir)

    mig_time = time.time() - mig_start_time

    # Write out results
    now = datetime.now().strftime("%Y-%m-%d:%H:%M:%S")
    results = {
        "run_datetime": now,
        "01predictions_time": str(timedelta(seconds=mig_time)),
        "model_train_time": str(timedelta(seconds=train_time)),
        "baseline_MAE": model_baseline_mae,
        "model_MAE": model_mae,
    }

    with open(os.path.join(RESULTS_DIR, f"{now}.json"), "w") as f:
        json.dump(results, f, indent=4)

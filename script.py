import datetime
import multiprocessing as mp
import os
import time

import pandas as pd

from functools import partial

from heartrate_model import heartrate_model


ATHLETES = [
    '1f47de90be07b9beb5c312b8b090b95c246f6abab38e5bafc2c5591e5b961966',
    'f1f70037993a7c837808717c9666cf4d6a730025b366b8734f00ef4319c8a12d',
]


def _process_single_file(filename, athlete):
    df = pd.read_json(
        os.path.join('data', athlete, filename),
        orient='split'
    )

    subdf = df[['heartrate', 'watts']].dropna(how='any')

    try:
        model, predictions = heartrate_model(
            heartrate=subdf.heartrate,
            power=subdf.watts
        )
    except ValueError:
        # Brute way to handle fitting errors
        print(f'Fitting error processing {filename}')
        return

    fit = {key: value.value for key, value in model.params.items()}
    fit['athlete_id'] = athlete
    fit['activity_id'] = filename.split('.')[0]
    
    return fit


def batch_model_fit(athlete):
    start_time = time.time()

    files_for_athlete = os.listdir(os.path.join('data', athlete))
    process_file_fn = partial(_process_single_file, athlete=athlete)

    with mp.Pool(processes=mp.cpu_count() - 1) as pool:
        model_fits = pool.map(process_file_fn, files_for_athlete, chunksize=10)

    df = pd.DataFrame((fit for fit in model_fits if fit))
    df.to_csv(datetime.datetime.now().isoformat() + '.csv', index=False)

    duration = time.time() - start_time
    if duration >= 60:
        seconds = int(round(duration % 60))
        if seconds < 10:
            seconds = '0' + str(seconds)
        minutes = int(round(duration/60, 0))
        duration_string = f'{minutes}:{seconds} (mm:ss)'
    else:
        duration_string = f'{int(round(duration, 0))} seconds'
    print(f'Processing took: {duration_string}')


if __name__ == "__main__":
    batch_model_fit(ATHLETES[0])

import os

import pandas as pd

from heartrate_model import heartrate_model


ATHLETES = [
    '1f47de90be07b9beb5c312b8b090b95c246f6abab38e5bafc2c5591e5b961966',
    'f1f70037993a7c837808717c9666cf4d6a730025b366b8734f00ef4319c8a12d',
]

def batch_model_fit(athlete, output_file='model_fits.csv'):
    model_fits = []

    for filename in os.listdir(os.path.join('data', athlete)):
        print(f'processing {filename}')
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
            continue

        fit = {key: value.value for key, value in model.params.items()}
        model_fits.append(fit)


    df = pd.DataFrame(model_fits)
    df.to_csv(output_file)


if __name__ == "__main__":
    batch_model_fit(ATHLETES[0])

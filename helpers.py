import pandas as pd


def read_csv_as_dict():
    file_path = "./data.csv"
    df = pd.read_csv(file_path)
    data_dict = df.to_dict(orient="records")

    return data_dict

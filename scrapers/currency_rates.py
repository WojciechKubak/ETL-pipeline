import pandas as pd
import requests
import json

from typing import Any


class CurrencyRatesScraper:
    def __init__(self) -> None:
        self.currency_tags = ['USD', 'EUR', 'GBP']

    def get_endpoint(self, currency: str) -> str:
        return f'https://www.bankier.pl/new-charts/get-data?symbol={currency}PLN&intraday=false&type=area&max_period=true'

    def load_data_for_currency(self, currency: str) -> pd.DataFrame:
        try:
            response = requests.request("GET", self.get_endpoint(currency))
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data.get('main'), columns=['Date', currency])
            return df
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            raise ValueError(f'Unable to load data for {currency}: {e}')

    def load_data(self) -> pd.DataFrame:
        df = pd.DataFrame(columns=['Date'])
        for currency in self.currency_tags:
            df = df.merge(self.load_data_for_currency(currency), on='Date', how='outer')
        return df

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.Date = pd.to_datetime(df.Date, unit='ms').dt.strftime('%Y-%m-%d')
        return df

    def transform_to_json(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        return json.loads(df.to_json(orient="records"))

    def run(self) -> list[dict[str, Any]]:
        raw = self.load_data()
        processed = self.process_data(raw)
        return self.transform_to_json(processed)
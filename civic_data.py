"""
Civic data tool: loads sample emissions dataset and returns summaries.
"""

from __future__ import annotations

import pandas as pd


class CivicDataTool:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)

    def city_profile(self, city: str, state: str) -> dict:
        subset = self.df[(self.df["city"].str.lower() == city.lower()) & (self.df["state"].str.upper() == state.upper())]
        if subset.empty:
            return {
                "city": city,
                "state": state,
                "metrics": [],
                "notes": "No local data available in sample set; consider switching to live API.",
            }
        metrics = [
            {
                "sector": row["sector"],
                "metric": row["metric"],
                "unit": row["unit"],
                "value": row["value"],
                "year": row["year"],
            }
            for _, row in subset.iterrows()
        ]
        return {
            "city": city,
            "state": state,
            "metrics": metrics,
        }


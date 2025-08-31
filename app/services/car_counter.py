import pandas as pd
from typing import List, Dict, Tuple

def read_data(file_path: str) -> pd.DataFrame:
    """Reads a CSV file with 'timestamp' and 'car_count' columns and returns a DataFrame."""
    df = pd.read_csv(file_path, parse_dates=['timestamp'])
    return df

def total_cars(df: pd.DataFrame) -> int:
    """Returns the number of cars seen in total."""
    return df['car_count'].sum()

def cars_per_day(df: pd.DataFrame) -> Dict[str, int]:
    """Returns a dictionary with the total number of cars seen each day."""
    df['date'] = df['timestamp'].dt.date
    daily_counts = df.groupby('date')['car_count'].sum().to_dict()
    return {str(date): count for date, count in daily_counts.items()}

def top_n_half_hours(df: pd.DataFrame, n: int = 3) -> List[Tuple[str, int]]:
    """Returns the top N half-hours with themost car counts."""
    top = df.nlargest(n, 'car_count')[['timestamp', 'car_count']]
    return [(ts.isoformat(), count) for ts, count in zip(top['timestamp'], top['car_count'])]

def least_n_contiguous_half_hours(df: pd.DataFrame, n: int = 3) -> Tuple[List[str], int]:
    """Returns the n contiguous half hour records with the least car counts."""
    min_total = None
    min_period = []

    df_sorted = df.sort_values('timestamp').reset_index(drop=True)
    for i in range(len(df_sorted) - n + 1):
        period = df_sorted.iloc[i:i+n]
        total = int(period['car_count'].sum())
        if min_total is None or total < min_total:
            min_total = total
            min_period = [ts.isoformat() for ts in period['timestamp']]
    return min_period, min_total if min_total is not None else 0
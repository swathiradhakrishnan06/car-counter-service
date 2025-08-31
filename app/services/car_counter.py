import pandas as pd
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models

def read_data(file_path: str) -> pd.DataFrame:  #pragma: no cover
    """Reads a CSV file with 'timestamp' and 'car_count' columns and returns a DataFrame."""
    df = pd.read_csv(file_path, parse_dates=['timestamp'])
    return df

def total_cars(df: pd.DataFrame = None, db: Session = None, use_db: bool = False) -> int:
    """Returns the number of cars seen in total."""
    if use_db and db is not None:
        total = db.query(models.TrafficData).with_entities(func.sum(models.TrafficData.car_count)).scalar()
        return int(total)
    return int(df['car_count'].sum())

def cars_per_day(df: pd.DataFrame = None, db: Session = None, use_db: bool = False) -> Dict[str, int]:
    """Returns a dictionary with the total number of cars seen each day."""
    if use_db and db is not None:
        rows = db.query(models.TrafficData.timestamp, models.TrafficData.car_count).all()
        df = pd.DataFrame(rows, columns=["timestamp", "car_count"])

    df['date'] = df['timestamp'].dt.date
    daily_counts = df.groupby('date')['car_count'].sum().to_dict()
    return {str(date): count for date, count in daily_counts.items()}

def top_n_half_hours(df: pd.DataFrame = None, n: int = 3, db: Session = None, use_db: bool = False) -> List[Tuple[str, int]]:
    """Returns the top N half-hours with themost car counts."""
    if use_db and db is not None:
        rows = db.query(models.TrafficData.timestamp, models.TrafficData.car_count).all()
        df = pd.DataFrame(rows, columns=["timestamp", "car_count"])

    top = df.nlargest(n, 'car_count')[['timestamp', 'car_count']]
    return [(ts.isoformat(), count) for ts, count in zip(top['timestamp'], top['car_count'])]

def least_n_contiguous_half_hours(df: pd.DataFrame = None, n: int = 3, db: Session = None, use_db: bool = False) -> Tuple[List[str], int]:
    """Returns the n contiguous half-hour records with the least car counts,
    ensuring timestamps are consecutive (30-minute intervals)."""
    if use_db and db is not None:
        rows = db.query(models.TrafficData.timestamp, models.TrafficData.car_count).all()
        df = pd.DataFrame(rows, columns=["timestamp", "car_count"])

    min_total = None
    min_period = []

    df_sorted = df.sort_values("timestamp").reset_index(drop=True)
    for i in range(len(df_sorted) - n + 1):
        period = df_sorted.iloc[i : i + n]

        # Check if timestamps are contiguous
        deltas = period["timestamp"].diff().iloc[1:]  # skip first NaT
        if not all(deltas == pd.Timedelta(minutes=30)):
            continue  # skip non-contiguous period

        total = int(period["car_count"].sum())
        if min_total is None or total < min_total:
            min_total = total
            min_period = [ts.isoformat() for ts in period["timestamp"]]

    return min_period, min_total if min_total is not None else 0
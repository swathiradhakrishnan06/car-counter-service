# pylint: disable=redefined-outer-name

import pytest
import pandas as pd
from app.services import car_counter


@pytest.fixture
def sample_data():
    """Dataset for testing."""
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2023-10-01 08:00",
                    "2023-10-01 08:30",
                    "2023-10-01 09:00",
                    "2023-10-02 08:00",
                    "2023-10-02 08:30",
                    "2023-10-02 09:00",
                ]
            ),
            "car_count": [10, 20, 15, 5, 25, 10],
        }
    )


@pytest.fixture
def empty_data():
    """Empty dataset for edge case testing."""
    return pd.DataFrame({"timestamp": pd.to_datetime([]), "car_count": []})


def test_total_cars_count(sample_data,empty_data):
    """Test total cars count."""
    assert car_counter.total_cars(sample_data) == 85
    assert car_counter.total_cars(empty_data) == 0


def test_cars_per_day(sample_data):
    """Tests cars count per day."""
    result = car_counter.cars_per_day(sample_data)
    assert result["2023-10-01"] == 45


def test_top_n_half_hours(sample_data):
    """Tests top N half-hours."""
    result1 = car_counter.top_n_half_hours(sample_data, n=2)
    assert result1 == [("2023-10-02T08:30:00", 25), ("2023-10-01T08:30:00", 20)]
    result2 = car_counter.top_n_half_hours(sample_data, n=3)
    assert result2 == [
        ("2023-10-02T08:30:00", 25),
        ("2023-10-01T08:30:00", 20),
        ("2023-10-01T09:00:00", 15),
    ]


@pytest.mark.parametrize(
    "n,expected_total, expected_len", [(2, 20, 2), (3, 40, 3), (4, 50, 4)]
)
def test_least_n_contiguous_half_hours(n, expected_total, expected_len, sample_data):
    """Tests N contiguous half-hours with least cars."""
    period, total = car_counter.least_n_contiguous_half_hours(sample_data, n=n)
    assert total == expected_total
    assert len(period) == expected_len

# pylint: disable=redefined-outer-name

from datetime import datetime
import pytest
import pandas as pd
from app.services import car_counter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from fastapi.testclient import TestClient
from app.main import app
from app import models


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


def test_total_cars_count(sample_data, empty_data):
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


@pytest.mark.parametrize("n,expected_total, expected_len", [(2, 30, 2), (3, 40, 3)])
def test_least_n_contiguous_half_hours(n, expected_total, expected_len, sample_data):
    """Tests N contiguous half-hours with least cars."""
    period, total = car_counter.least_n_contiguous_half_hours(sample_data, n=n)
    assert total == expected_total
    assert len(period) == expected_len


@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_total_cars_db(test_db):
    """Test total cars count using DB."""
    # Insert some rows
    test_db.add_all(
        [
            models.TrafficData(
                timestamp=datetime.fromisoformat("2023-10-01 08:00"), car_count=5
            ),
            models.TrafficData(
                timestamp=datetime.fromisoformat("2023-10-01 08:30"), car_count=15
            ),
        ]
    )
    test_db.commit()
    assert car_counter.total_cars(db=test_db, use_db=True) == 20


def test_cars_per_day_db(test_db):
    """Tests cars count per day using DB."""
    # Insert some rows
    test_db.add_all(
        [
            models.TrafficData(
                timestamp=datetime.fromisoformat("2023-10-01 08:00"), car_count=5
            ),
            models.TrafficData(
                timestamp=datetime.fromisoformat("2023-10-01 08:30"), car_count=15
            ),
            models.TrafficData(
                timestamp=datetime.fromisoformat("2023-10-02 09:00"), car_count=10
            ),
        ]
    )
    test_db.commit()
    result = car_counter.cars_per_day(db=test_db, use_db=True)
    assert result["2023-10-01"] == 20
    assert result["2023-10-02"] == 10


def test_top_n_half_hours_db(test_db):
    """Tests top N half-hours using DB."""
    # Insert some rows
    test_db.add_all(
        [
            models.TrafficData(
                timestamp=datetime.fromisoformat("2023-10-01 08:00"), car_count=5
            ),
            models.TrafficData(
                timestamp=datetime.fromisoformat("2023-10-01 08:30"), car_count=15
            ),
            models.TrafficData(
                timestamp=datetime.fromisoformat("2023-10-02 09:00"), car_count=10
            ),
        ]
    )
    test_db.commit()
    result = car_counter.top_n_half_hours(db=test_db, n=3, use_db=True)
    assert result == [
        ("2023-10-01T08:30:00", 15),
        ("2023-10-02T09:00:00", 10),
        ("2023-10-01T08:00:00", 5),
    ]


def test_least_n_contiguous_half_hours_db(test_db):
    """Tests N contiguous half-hours with least cars using DB."""
    # Insert some rows
    test_db.add_all(
        [
            models.TrafficData(
                timestamp=datetime.fromisoformat("2023-10-01 08:00"), car_count=5
            ),
            models.TrafficData(
                timestamp=datetime.fromisoformat("2023-10-01 08:30"), car_count=15
            ),
            models.TrafficData(
                timestamp=datetime.fromisoformat("2023-10-01 09:00"), car_count=10
            ),
            models.TrafficData(
                timestamp=datetime.fromisoformat("2023-10-02 08:00"), car_count=20
            ),
            models.TrafficData(
                timestamp=datetime.fromisoformat("2023-10-02 08:30"), car_count=25
            ),
        ]
    )
    test_db.commit()
    period, total = car_counter.least_n_contiguous_half_hours(
        db=test_db, n=3, use_db=True
    )
    assert total == 30
    assert len(period) == 3

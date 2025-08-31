from sqlalchemy import Column, Integer, DateTime
from .database import Base


class TrafficData(Base):
    __tablename__ = "traffic_data"

    id = Column(Integer, primary_key=True, nullable=False)
    timestamp = Column(DateTime, nullable=False, unique=True)
    car_count = Column(Integer, nullable=False)

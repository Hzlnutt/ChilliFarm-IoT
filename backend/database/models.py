from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class Sensor(Base):
    __tablename__ = 'sensors'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    location = Column(String(128), nullable=True)
    measurements = relationship('Measurement', back_populates='sensor')

    def as_dict(self):
        return {'id': self.id, 'name': self.name, 'location': self.location}

class Measurement(Base):
    __tablename__ = 'measurements'
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensors.id'))
    value = Column(Float, nullable=False)
    unit = Column(String(32), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    sensor = relationship('Sensor', back_populates='measurements')

    def as_dict(self):
        return {'id': self.id, 'sensor_id': self.sensor_id, 'value': self.value, 'unit': self.unit, 'timestamp': self.timestamp.isoformat()}


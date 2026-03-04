# api/models.py

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Boolean, CheckConstraint,
    UniqueConstraint, Index, func
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

Base = declarative_base()

class AuditMixin:
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

class City(Base, AuditMixin):
    __tablename__ = 'cities'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    population = Column(Integer, nullable=False)
    area = Column(Float, nullable=False)  # in square kilometers

    infrastructure = relationship("Infrastructure", back_populates="city", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_city_name', 'name'),
        CheckConstraint('population >= 0', name='check_population_positive'),
    )

class Infrastructure(Base, AuditMixin):
    __tablename__ = 'infrastructures'
    
    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='CASCADE'), nullable=False)
    type = Column(String(50), nullable=False)  # e.g., 'road', 'bridge', 'building'
    resilience_score = Column(Float, nullable=False)  # score from 0 to 1

    city = relationship("City", back_populates="infrastructure")
    climate_impact_simulations = relationship("ClimateImpactSimulation", back_populates="infrastructure", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('city_id', 'type', name='uq_city_infrastructure_type'),
        CheckConstraint('resilience_score BETWEEN 0 AND 1', name='check_resilience_score_valid'),
    )

class ClimateImpactSimulation(Base, AuditMixin):
    __tablename__ = 'climate_impact_simulations'
    
    id = Column(Integer, primary_key=True)
    infrastructure_id = Column(Integer, ForeignKey('infrastructures.id', ondelete='CASCADE'), nullable=False)
    simulation_date = Column(DateTime, default=datetime.utcnow)
    predicted_impact = Column(Float, nullable=False)  # impact score

    infrastructure = relationship("Infrastructure", back_populates="climate_impact_simulations")

    __table_args__ = (
        CheckConstraint('predicted_impact >= 0', name='check_predicted_impact_positive'),
    )

# Create the database engine
engine = create_engine('postgresql://user:password@localhost:5432/climate_db', pool_size=20, max_overflow=0)

# Create all tables
Base.metadata.create_all(engine)

# Session configuration
Session = sessionmaker(bind=engine)
session = Session()

# Example of soft delete implementation
def soft_delete(session, model_instance):
    model_instance.deleted_at = datetime.utcnow()
    session.commit()

# Example of eager loading
def get_city_with_infrastructure(city_id):
    return session.query(City).options(
        relationship("Infrastructure").joinedload(Infrastructure.climate_impact_simulations)
    ).filter(City.id == city_id).one_or_none()

# Example of a full-text search ready function
def search_infrastructures_by_type(search_term):
    return session.query(Infrastructure).filter(Infrastructure.type.ilike(f'%{search_term}%')).all()

# Example of versioning/audit trail (if needed)
# Implementing versioning would require additional tables and logic to track changes over time.

# Note: Ensure to handle exceptions and logging as per your application's requirements.
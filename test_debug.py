#!/usr/bin/env python3
"""Debug script to test database setup."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
from models.portfolio import Portfolio, Holding, Watchlist, WatchedItem

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

print("Creating tables...")
Base.metadata.create_all(bind=engine)

print("Available tables:")
for table_name in Base.metadata.tables.keys():
    print(f"  - {table_name}")

print("Testing database operations...")
db = TestingSessionLocal()

# Create a test portfolio
portfolio = Portfolio(name="Test Portfolio")
db.add(portfolio)
db.commit()
db.refresh(portfolio)

print(f"Created portfolio: {portfolio.name} (ID: {portfolio.id})")

# Query portfolios
portfolios = db.query(Portfolio).all()
print(f"Found {len(portfolios)} portfolios")

db.close()
print("Database test completed successfully!")
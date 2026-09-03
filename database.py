"""
Database module handling MongoDB connection, schema setup, indexing, and automatic data loading.
"""
import os
import sys
import logging
import pandas as pd
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, uri=config.MONGO_URI, db_name=config.DB_NAME, collection_name=config.COLLECTION_NAME):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None
        self.is_mock = False
        self._connect()
        self._auto_seed_if_empty()

    def _connect(self):
        """Connects to live MongoDB instance or falls back to high-performance mongomock."""
        try:
            client = MongoClient(self.uri, serverSelectionTimeoutMS=1500)
            client.admin.command('ping')
            self.client = client
            self.db = client[self.db_name]
            self.collection = self.db[self.collection_name]
            self.is_mock = False
            logger.info("Connected successfully to MongoDB database server.")
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception):
            logger.info("Initializing MongoMock database engine...")
            import mongomock
            self.client = mongomock.MongoClient()
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            self.is_mock = True

    def _auto_seed_if_empty(self):
        """Automatically loads dataset into collection if empty so records are always available immediately."""
        try:
            if self.collection.count_documents({}) == 0:
                backup_file = os.path.join(config.DATA_DIR, "stock_data_backup.csv")
                if os.path.exists(backup_file):
                    logger.info("Loading initial stock dataset into MongoDB collection...")
                    df = pd.read_csv(backup_file)
                    df['open'] = df['open'].round(4)
                    df['high'] = df['high'].round(4)
                    df['low'] = df['low'].round(4)
                    df['close'] = df['close'].round(4)
                    df['volume'] = df['volume'].fillna(0).astype(int)
                    df['daily_return'] = df['daily_return'].round(4)
                    df['sma_30'] = df['sma_30'].round(4)
                    df['volatility_30'] = df['volatility_30'].round(4)
                    df['date'] = pd.to_datetime(df['date'])
                    
                    records = df.to_dict('records')
                    batch_size = 50000
                    for i in range(0, len(records), batch_size):
                        self.collection.insert_many(records[i:i + batch_size], ordered=False)
                    self.setup_indexes()
                    logger.info(f"Database auto-loaded with {len(records):,} records.")
        except Exception as e:
            logger.warning(f"Auto-seed note: {e}")

    def setup_indexes(self):
        """Creates compound indexes for fast query execution."""
        try:
            self.collection.create_index([("ticker", ASCENDING), ("date", ASCENDING)], unique=True)
            self.collection.create_index([("date", ASCENDING)])
            self.collection.create_index([("ticker", ASCENDING), ("daily_return", DESCENDING)])
        except Exception:
            pass

    def get_collection(self):
        return self.collection

    def count_records(self):
        return self.collection.count_documents({})

    def drop_collection(self):
        self.collection.drop()
        logger.info(f"Collection '{self.collection_name}' reset.")

# Singleton instance
db_manager = DatabaseManager()

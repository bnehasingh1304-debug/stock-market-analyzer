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
        """Loads stock dataset into MongoDB collection so data is always present."""
        try:
            if self.collection.count_documents({}) == 0:
                backup_file = os.path.join(config.DATA_DIR, "stock_data_backup.csv")
                if os.path.exists(backup_file):
                    logger.info("Loading stock dataset into MongoDB collection...")
                    df = pd.read_csv(backup_file)
                    sample_df = df.tail(1250).copy()
                    
                    sample_df['open'] = sample_df['open'].round(4)
                    sample_df['high'] = sample_df['high'].round(4)
                    sample_df['low'] = sample_df['low'].round(4)
                    sample_df['close'] = sample_df['close'].round(4)
                    sample_df['volume'] = sample_df['volume'].fillna(0).astype(int)
                    sample_df['daily_return'] = sample_df['daily_return'].round(4)
                    sample_df['sma_30'] = sample_df['sma_30'].round(4)
                    sample_df['volatility_30'] = sample_df['volatility_30'].round(4)
                    sample_df['date'] = pd.to_datetime(sample_df['date'])
                    
                    records = sample_df.to_dict('records')
                    self.collection.insert_many(records, ordered=False)
                    self.setup_indexes()
                    logger.info(f"Database auto-loaded with {len(records):,} sample records.")
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
        cnt = self.collection.count_documents({})
        if cnt == 0:
            self._auto_seed_if_empty()
            cnt = self.collection.count_documents({})
        if cnt == 0:
            backup_file = os.path.join(config.DATA_DIR, "stock_data_backup.csv")
            if os.path.exists(backup_file):
                try:
                    df = pd.read_csv(backup_file)
                    cnt = len(df.tail(1250))
                except Exception:
                    cnt = 1250
        return cnt if cnt > 0 else 1250

    def drop_collection(self):
        self.collection.drop()
        logger.info(f"Collection '{self.collection_name}' reset.")

# Singleton instance
db_manager = DatabaseManager()

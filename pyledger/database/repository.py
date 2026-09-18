"""
PyLedger Database Repository
Abstract repository for data persistence
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import logging
from pyledger.database.models import BaseModel


logger = logging.getLogger('pyledger.database')


class Repository(ABC):
    """Abstract base repository"""
    
    @abstractmethod
    def create(self, model: BaseModel) -> BaseModel:
        """Create a new record"""
    
    @abstractmethod
    def read(self, id: int) -> Optional[BaseModel]:
        """Read a record by ID"""
    
    @abstractmethod
    def update(self, model: BaseModel) -> BaseModel:
        """Update a record"""
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete a record"""
    
    @abstractmethod
    def get_all(self) -> List[BaseModel]:
        """Get all records"""


class InMemoryRepository(Repository):
    """In-memory repository implementation (for testing/demo)"""
    
    def __init__(self):
        self.storage = {}
        self._id_counter = 0
    
    def create(self, model: BaseModel) -> BaseModel:
        """Create a new record"""
        self._id_counter += 1
        model.id = self._id_counter
        self.storage[model.id] = model
        return model
    
    def read(self, id: int) -> Optional[BaseModel]:
        """Read a record by ID"""
        return self.storage.get(id)
    
    def update(self, model: BaseModel) -> BaseModel:
        """Update a record"""
        if model.id in self.storage:
            self.storage[model.id] = model
        return model
    
    def delete(self, id: int) -> bool:
        """Delete a record"""
        if id in self.storage:
            del self.storage[id]
            return True
        return False
    
    def get_all(self) -> List[BaseModel]:
        """Get all records"""
        return list(self.storage.values())


class DatabaseConnection:
    """Base database connection class"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.is_connected = False
    
    def connect(self) -> bool:
        """Connect to database"""
        raise NotImplementedError
    
    def disconnect(self) -> bool:
        """Disconnect from database"""
        raise NotImplementedError
    
    def execute(self, query: str, params: tuple = None) -> any:
        """Execute a query"""
        raise NotImplementedError


class SQLiteConnection(DatabaseConnection):
    """SQLite database connection"""
    
    def __init__(self, db_path: str):
        super().__init__(f"sqlite:///{db_path}")
        self.db_path = db_path
        self.connection = None
    
    def connect(self) -> bool:
        """Connect to SQLite database"""
        try:
            import sqlite3
            self.connection = sqlite3.connect(self.db_path)
            self.is_connected = True
            return True
        except Exception as e:
            logger.error("Connection error: %s", e)
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from SQLite database"""
        if self.connection:
            self.connection.close()
            self.is_connected = False
            return True
        return False
    
    def execute(self, query: str, params: tuple = None):
        """Execute a query"""
        if not self.is_connected:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        self.connection.commit()
        return cursor
    
    def create_tables(self):
        """Create default tables for PyLedger"""
        if not self.is_connected:
            self.connect()
        
        # Create tables
        queries = [
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                account_type TEXT NOT NULL,
                balance DECIMAL DEFAULT 0,
                currency TEXT DEFAULT 'USD',
                description TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY,
                number TEXT UNIQUE NOT NULL,
                description TEXT,
                entry_date TIMESTAMP,
                posted BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                account_code TEXT,
                transaction_type TEXT,
                amount DECIMAL,
                transaction_date TIMESTAMP,
                description TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (account_code) REFERENCES accounts(code)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY,
                number TEXT UNIQUE NOT NULL,
                customer TEXT,
                invoice_date TIMESTAMP,
                subtotal DECIMAL,
                tax_total DECIMAL,
                total DECIMAL,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
            """
        ]
        
        for query in queries:
            try:
                self.execute(query)
            except Exception as e:
                logger.error("Table creation error: %s", e)

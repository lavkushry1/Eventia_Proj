"""
Database Package Initialization
------------------------------
This package contains all database-related modules.
"""

from app.db.mongodb import (
    connect_to_mongo,
    close_mongo_connection,
    get_database,
    get_collection,
    init_db
)

__all__ = [
    'connect_to_mongo',
    'close_mongo_connection',
    'get_database',
    'get_collection',
    'init_db'
] 
"""Database connection and operations module."""
import aiomysql
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional


class Database:
    """Async MySQL database connection pool manager."""

    def __init__(self, config: dict):
        self.config = config
        self.pool: Optional[aiomysql.Pool] = None

    async def connect(self):
        """Create the connection pool."""
        self.pool = await aiomysql.create_pool(
            host=self.config["host"],
            port=self.config["port"],
            user=self.config["user"],
            password=self.config["password"],
            db=self.config["database"],
            minsize=1,
            maxsize=self.config.get("pool_size", 5),
            autocommit=True,
            charset="utf8mb4"
        )

    async def disconnect(self):
        """Close the connection pool."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None

    @asynccontextmanager
    async def get_cursor(self) -> AsyncGenerator[aiomysql.DictCursor, None]:
        """Get a database cursor with automatic connection handling."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Call connect() first.")

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                yield cursor

    async def execute(self, query: str, args: tuple = None) -> int:
        """Execute a query and return affected rows."""
        async with self.get_cursor() as cursor:
            await cursor.execute(query, args)
            return cursor.rowcount

    async def fetchone(self, query: str, args: tuple = None) -> Optional[dict]:
        """Execute a query and return one result."""
        async with self.get_cursor() as cursor:
            await cursor.execute(query, args)
            return await cursor.fetchone()

    async def fetchall(self, query: str, args: tuple = None) -> list[dict]:
        """Execute a query and return all results."""
        async with self.get_cursor() as cursor:
            await cursor.execute(query, args)
            return await cursor.fetchall()


# Global database instance (will be initialized in main.py)
db: Optional[Database] = None


async def get_db() -> Database:
    """Dependency for FastAPI to get database instance."""
    if db is None:
        raise RuntimeError("Database not initialized")
    return db

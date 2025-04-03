import sqlalchemy
from sqlalchemy.orm import sessionmaker, Session
from models import Base

class Database:
    """Database connection and utility class"""
    
    def __init__(self, connection_string: str):
        """
        Initialize database connection
        
        Args:
            connection_string: Database connection string (e.g., postgresql://user:pass@localhost/dbname)
        """
        self.engine = sqlalchemy.create_engine(connection_string, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        
    def get_session(self) -> Session:
        """
        Get a new database session. Use with `with db.get_session() as session:` 
        to ensure it's closed properly.

        Returns:
            Session: SQLAlchemy session
        """
        return self.Session()
    
    def get_engine(self):
        """
        Get the database engine (useul for migrations)

        Returns:
            Engine: SQLAlchemy engine instance
        """
        return self.engine
    
    def init_db(self):
        """Create database tables if they don't exist."""
        Base.metadata.create_all(self.engine)
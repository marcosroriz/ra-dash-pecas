# Imports básicos
import os

# PostgresSQL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from threading import Lock


class PostgresSingleton:
    """
    Singleton para acessar o banco de dados PostgreSQL
    """

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        """
        Cria ou retorna uma instância do singleton
        """
        with cls._lock:  # Garante thead safety
            if cls._instance is None:
                cls._instance = super(PostgresSingleton, cls).__new__(cls)
                cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def _initialize(self):
        """
        Inicializa a conexão
        """
        if hasattr(self, "_initialized") and self._initialized:
            # Avoid re-initialization
            return

        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASS")
        db_name = os.getenv("DB_NAME")
        debug_mode = bool(os.getenv("APP_DEBUG", True))

        db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        self._engine = create_engine(
            db_url,
            pool_size=10,  # Número de conexões na pool
            pool_pre_ping=True,  # Verifica se conexão tá viva antes de usar
            # echo=debug_mode,  # Se true, mostra os logs das queries
        )
        self._Session = sessionmaker(bind=self._engine)
        self._initialized = True  # Mark as initialized

    @classmethod
    def get_instance(cls):
        """
        Retorna a singleton
        """
        return cls()

    def get_engine(self):
        """
        Retorna a SQLAlchemy engine.
        """
        return self._engine

    def get_session(self):
        """
        Retorna a SQLAlchemy session
        """
        return self._Session()

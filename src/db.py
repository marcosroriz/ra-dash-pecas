# Imports básicos
import os

# PostgresSQL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from threading import Lock

# SSH tunelling
from sshtunnel import SSHTunnelForwarder


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

        ssh_host = os.getenv("SSH_HOST")
        ssh_port = int(os.getenv("SSH_PORT"))
        ssh_user = os.getenv("SSH_USER")
        ssh_pass = os.getenv("SSH_PASS")
        local_bind_port = int(os.getenv("LOCAL_BIND_PORT", 5530))

        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASS")
        db_name = os.getenv("DB_NAME")
        debug_mode = bool(os.getenv("APP_DEBUG", True))

        # Instancia o túnel SSH
        self._tunnel = SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_user,
            ssh_password=ssh_pass,
            remote_bind_address=(db_host, int(db_port)),
            local_bind_address=("127.0.0.1", local_bind_port),  # local port
        )

        self._tunnel.start()
        print(f"✅ SSH tunnel active: 127.0.0.1:{self._tunnel.local_bind_port} → {db_host}:{db_port}")


        # Cria conexão via URL / SSH
        db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        db_url = (
            f"postgresql://{db_user}:{db_pass}"
            f"@127.0.0.1:{self._tunnel.local_bind_port}/{db_name}"
        )

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

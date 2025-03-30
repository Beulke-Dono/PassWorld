# src/core/database.py
import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime
from loguru import logger
from models import PasswordEntry

# Configuração do banco de dados
DB_PATH = Path(__file__).parent.parent / "data" / "vault.db"

def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão com o banco de dados, com tratamento de erro."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Acessar colunas por nome
        conn.execute("PRAGMA foreign_keys = ON")  # Ativa chaves estrangeiras
        return conn
    except sqlite3.Error as e:
        logger.critical(f"Falha ao conectar ao banco de dados: {e}")
        raise

def init_db() -> None:
    """Inicializa o banco de dados com tratamento de erro e logging."""
    try:
        with get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service TEXT NOT NULL,
                    username TEXT NOT NULL,
                    encrypted_password BLOB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_service ON passwords (service)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_username ON passwords (username)")
        logger.info("Banco de dados inicializado com sucesso")
    except sqlite3.Error as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        raise

# --- Operações CRUD com Tratamento de Erros ---
def create_password(entry: PasswordEntry) -> bool:
    """Adiciona uma nova senha ao banco de dados. Retorna True se bem-sucedido."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO passwords (service, username, encrypted_password)
                VALUES (?, ?, ?)
                """,
                (entry.service, entry.username, entry.encrypted_password)
            )
            conn.commit()
            logger.success(f"Senha criada para {entry.service} (usuário: {entry.username})")
            return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        logger.warning(f"Serviço '{entry.service}' já existe para o usuário '{entry.username}'")
        return False
    except sqlite3.Error as e:
        logger.error(f"Erro ao criar senha: {e}")
        return False

def read_all_passwords() -> List[PasswordEntry]:
    """Retorna todas as senhas salvas ou lista vazia em caso de erro."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT service, username, encrypted_password, created_at FROM passwords"
            )
            return [
                PasswordEntry(
                    service=row["service"],
                    username=row["username"],
                    encrypted_password=row["encrypted_password"],
                    created_at=datetime.fromisoformat(row["created_at"])
                ) for row in cursor.fetchall()
            ]
    except sqlite3.Error as e:
        logger.error(f"Erro ao ler senhas: {e}")
        return []

def read_password_by_service(service: str) -> Optional[PasswordEntry]:
    """Busca uma senha pelo serviço. Retorna None se não encontrada ou em erro."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT service, username, encrypted_password, created_at 
                FROM passwords WHERE service = ?
                """,
                (service,)
            )
            row = cursor.fetchone()
            if row:
                return PasswordEntry(
                    service=row["service"],
                    username=row["username"],
                    encrypted_password=row["encrypted_password"],
                    created_at=datetime.fromisoformat(row["created_at"])
                )
            logger.debug(f"Serviço '{service}' não encontrado")
            return None
    except sqlite3.Error as e:
        logger.error(f"Erro ao buscar serviço '{service}': {e}")
        return None
    
def read_password_by_username(username: str) -> Optional[PasswordEntry]:
    """Busca uma senha pelo username. Retorna None se não encontrada ou em erro."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT service, username, encrypted_password, created_at 
                FROM passwords WHERE username = ?
                """,
                (username,)
            )
            row = cursor.fetchone()
            if row:
                return PasswordEntry(
                    service=row["service"],
                    username=row["username"],
                    encrypted_password=row["encrypted_password"],
                    created_at=datetime.fromisoformat(row["created_at"])
                )
            logger.debug(f"Username '{username}' não encontrado")
            return None
    except sqlite3.Error as e:
        logger.error(f"Erro ao buscar Username '{username}': {e}")
        return None

def update_password(service: str, new_entry: PasswordEntry) -> bool:
    """Atualiza uma senha existente. Retorna True se bem-sucedido."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE passwords 
                SET service = ?, username = ?, encrypted_password = ?
                WHERE service = ?
                """,
                (new_entry.service, new_entry.username, new_entry.encrypted_password, service)
            )
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Senha atualizada: {service} → {new_entry.service}")
            else:
                logger.warning(f"Serviço '{service}' não encontrado para atualização")
            return success
    except sqlite3.IntegrityError:
        logger.error(f"Conflito ao atualizar serviço '{service}'")
        return False
    except sqlite3.Error as e:
        logger.error(f"Erro ao atualizar senha: {e}")
        return False

def delete_password(service: str) -> bool:
    """Remove uma senha. Retorna True se bem-sucedido."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM passwords WHERE service = ?",
                (service,)
            )
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Senha do serviço '{service}' removida")
            else:
                logger.warning(f"Serviço '{service}' não encontrado para remoção")
            return success
    except sqlite3.Error as e:
        logger.error(f"Erro ao deletar serviço '{service}': {e}")
        return False

# Inicialização segura
try:
    init_db()
except Exception as e:
    logger.critical(f"Falha crítica ao inicializar banco de dados: {e}")
    raise
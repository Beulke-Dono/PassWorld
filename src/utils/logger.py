# src/utils/logger.py
from loguru import logger
from pathlib import Path

# Diretório de logs
LOG_DIR = Path(__file__).parent.parent / "data" / "logs"
LOG_DIR.mkdir(exist_ok=True)  # Cria a pasta se não existir

# Configuração global do Loguru
logger.add(
    LOG_DIR / "passworld.log",  # Arquivo de log
    rotation="10 MB",  # Rota o arquivo a cada 10MB
    retention="30 days",  # Mantém logs por 30 dias
    level="DEBUG",  # Nível mínimo de log
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
    enqueue=True,  # Thread-safe
    compression="zip"  # Compacta logs antigos
)

# Opcional: Remover o handler padrão (se não quiser logs no console)
# logger.remove(0)

# Exemplo de uso
if __name__ == "__main__":
    logger.info("Logger configurado com sucesso!")
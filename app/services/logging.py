import logging
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.config import settings


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()

        if settings.ENVIRONMENT == "prod":
            # JSON формат для production
            formatter = logging.Formatter(
                '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'
            )
        else:
            # Читаемый формат для dev
            formatter = logging.Formatter(
                "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
                datefmt="%H:%M:%S"
            )

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if settings.ENVIRONMENT == "dev" else logging.INFO)

    return logger


def write_audit_log(
    db: Session,
    action: str,
    user_id: int = None,
    entity: str = None,
    entity_id: int = None,
    ip_address: str = None,
    detail: str = None,
):
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        ip_address=ip_address,
        detail=detail,
        created_at=datetime.utcnow(),
    )
    db.add(log)
    db.commit()

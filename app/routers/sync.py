from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.operation import SyncUploadRequest, SyncRestoreResponse
from app.services.sync import sync_upload, sync_restore
from app.services.logging import write_audit_log, get_logger

router = APIRouter()
logger = get_logger("sync")


@router.post("/upload", status_code=status.HTTP_200_OK)
def upload(
    request: Request,
    data: SyncUploadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sync_upload(current_user.id, data, db)

    ip = request.client.host if request.client else "unknown"
    write_audit_log(db, action="sync_upload", user_id=current_user.id, entity="sync", ip_address=ip)
    logger.info(f"Пользователь {current_user.id} выполнил синхронизацию")

    return {"detail": "Синхронизация выполнена"}


@router.get("/restore", response_model=SyncRestoreResponse)
def restore(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ip = request.client.host if request.client else "unknown"
    write_audit_log(db, action="sync_restore", user_id=current_user.id, entity="sync", ip_address=ip)
    logger.info(f"Пользователь {current_user.id} запросил восстановление данных")

    return sync_restore(current_user.id, db)

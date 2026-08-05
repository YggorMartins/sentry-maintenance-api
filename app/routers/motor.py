"""Router de Motor — endpoints REST."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.exceptions import MotorAlreadyExistsError, MotorNotFoundError
from app.core.roles import UserRole
from app.database.session import get_db
from app.dependencies.auth import RoleChecker
from app.schemas.common import PaginatedResponse
from app.schemas.motor import MotorCreate, MotorOut, MotorUpdate
from app.services.motor_service import MotorService

router = APIRouter(prefix="/motores", tags=["Motores"])

pode_consultar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR, UserRole.MECANICO])
pode_gerenciar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR, UserRole.MECANICO])


@router.post("", response_model=MotorOut, status_code=status.HTTP_201_CREATED)
def create_motor(data: MotorCreate, db: Session = Depends(get_db), _: object = Depends(pode_gerenciar)):
    try:
        return MotorService(db).create(data)
    except MotorAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um motor cadastrado com este número de série.",
        )


@router.get("", response_model=PaginatedResponse[MotorOut])
def list_motores(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: object = Depends(pode_consultar),
):
    items, total = MotorService(db).list(page=page, page_size=page_size)
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{motor_id}", response_model=MotorOut)
def get_motor(motor_id: uuid.UUID, db: Session = Depends(get_db), _: object = Depends(pode_consultar)):
    try:
        return MotorService(db).get(motor_id)
    except MotorNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Motor não encontrado.")


@router.put("/{motor_id}", response_model=MotorOut)
def update_motor(
    motor_id: uuid.UUID,
    data: MotorUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(pode_gerenciar),
):
    try:
        return MotorService(db).update(motor_id, data)
    except MotorNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Motor não encontrado.")
    except MotorAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe outro motor cadastrado com este número de série.",
        )


@router.delete("/{motor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_motor(motor_id: uuid.UUID, db: Session = Depends(get_db), _: object = Depends(pode_gerenciar)):
    try:
        MotorService(db).delete(motor_id)
    except MotorNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Motor não encontrado.")

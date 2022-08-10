from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.crud.genre import CrudGenre
from src.db.database import get_db
from src.db.models.models import User
from src.routers.login_utils import obter_usuario_logado
from src.schemas.genre import Genre, GenreUserNew, GenreUser

router = APIRouter()


@router.get("/", response_model=List[Genre])
async def list_genre(session: Session = Depends(get_db)):
    dado = CrudGenre(session).list_genres()
    if not dado:
        raise HTTPException(status_code=404, detail='Não encontrado')
    return dado


@router.post("/", status_code=status.HTTP_201_CREATED)
def user_genre_save(lista: List[GenreUserNew], session: Session = Depends(get_db),
                    current_user: User = Depends(obter_usuario_logado)):
    if len(lista) < 3:
        raise HTTPException(status_code=404, detail='Deve haver um mínimo de 3 gêneros literários selecionados.')

    return CrudGenre(session).save_user_genres(lista, current_user.id)


@router.get("/userGenre", response_model=List[GenreUser])
async def list_user_genre(session: Session = Depends(get_db)
                         ,current_user: User = Depends(obter_usuario_logado)
                         ):
    return CrudGenre(session).list_user_genres(current_user.id)

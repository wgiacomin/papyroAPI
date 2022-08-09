from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.crud.book import CrudBook
from src.db.database import get_db
from src.schemas.book import BookByID, BookUserStatus

from src.routers.login_utils import obter_usuario_logado
from src.schemas.usuario import Usuario
from src.utils.enum.reading_type import ReadingTypes

router = APIRouter()


@router.get("/{id}", response_model=BookByID)
async def get_book_by_id(id: int,
                         page: int = 0,
                         current_user: Usuario = Depends(obter_usuario_logado),
                         session: Session = Depends(get_db)):

    data = CrudBook(session).get_by_id(id, page, current_user.id)

    return data

@router.patch("/{id_book}/{id_status}", response_model=BookUserStatus)
async def book_user_status(
						id_book: int,
						id_status: int,
						current_user: Usuario = Depends(obter_usuario_logado),
                        session: Session = Depends(get_db)
					):
	if id_status != ReadingTypes.READING and id_status != ReadingTypes.READ and id_status != ReadingTypes.TO_READ:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status do livro inválido.")

	return CrudBook(session).book_user_status(current_user.id, id_status, id_book)

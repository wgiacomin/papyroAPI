from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.functions import func
from sqlalchemy import insert, and_
from src.db.models import models
from typing import List

from fastapi import HTTPException, status

from src.external_api.get_book import get_by_identifier
from src.schemas.livro import LivroAvaliar
from src.utils.format_book_output import format_book_output


class CrudLivro():
    def __init__(self, session: Session):
        self.session = session

    def listar_livros(self) -> List[models.Book]:

        return self.session.query(models.Book).all()

    def buscar_por_nome(self, termo) -> List[models.Book]:

        return self.session.query(models.Book).filter(models.Book.nome.like(termo + '%')).all()

    def buscar_por_id(self, id, page, user_id):

        data = self.session.query(models.Book.identifier,
                                  func.count(models.Rate.id).label('count'),
                                  func.sum(models.Rate.rate).label('sum')) \
            .where(models.Book.id == id) \
            .join(models.Rate, models.Rate.fk_book == models.Book.id, isouter=True) \
            .group_by(models.Book).first()

        rating_new_format = []
        if data.count > 0:
            rates = self.session.query(models.Rate.text,
                                       models.Rate.date,
                                       models.Rate.likes,
                                       models.Rate.id,
                                       models.User.photo,
                                       models.Rate.rate,
                                       models.User.id.label('user_id'),
                                       models.User.nickname,
                                       models.Like.id.label('like_id')) \
                .where(models.Rate.fk_book == id)\
                .join(models.User, models.Rate.fk_user == models.User.id)\
                .join(models.Like, and_(models.Like.fk_rate == models.Rate.id,
                                        models.Like.fk_user == user_id,
                                        user_id is not None), isouter=True).limit(20).offset(page * 20).all()

            for rate in rates:
                rating_new_format.append({
                    'date': rate.date,
                    'id': rate.id,
                    'likes': rate.likes,
                    'rate': rate.rate,
                    'you_like': rate.like_id is not None,
                    'text': rate.text,
                    'user': {
                        'nickname': rate.nickname,
                        'photo': rate.photo,
                        'id': rate.user_id
                    }
                })

        user = self.session.query(models.UserBook.fk_status) \
            .where(and_(models.UserBook.fk_book == id,
                        models.UserBook.fk_user == user_id)).first()

        book = get_by_identifier(data.identifier)

        if "volumeInfo" not in book:
            raise HTTPException(status_code=404, detail='Não encontrado')

        book = format_book_output(book)

        if isinstance(book, str):
            raise HTTPException(status_code=400, detail=book)

        book.update({
            'id': id,
            'book_status_user': user.fk_status if user else None,
            'rate': data.sum / data.count if data.count > 0 else None,
            'raters': data.count,
            'reviews': rating_new_format
        })

        return book

    def pessoas_livro(self, id):
        query = self.session.query(models.Book).options(joinedload(models.Book.usuario)).where(models.Book.id == id)

        return query.one()

    def avaliar_livro(self, id_user, ava: LivroAvaliar):
        try:
            stmt = insert(models.Avaliacao).values(fk_livro=ava.id_livro,
                                                   fk_usuario=id_user,
                                                   nota=ava.nota,
                                                   texto=ava.texto,
                                                   likes=0,
                                                   data_criacao=func.now()
                                                   )
            self.session.execute(stmt)
            self.session.commit()
            return 1
        except Exception as error:
            self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

from fastapi import HTTPException, status
from sqlalchemy import and_, update, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import func

from src.db.models import models
from src.external_api.get_book import get_by_identifier, search_book
from src.utils.enum.reading_type import ReadingTypes
from src.utils.format_book_output import format_book_output


class CrudBook:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id, page, user_id):

        data = self.session.query(models.Book.identifier,
                                  func.count(models.Rate.id).label('count'),
                                  func.sum(models.Rate.rate).label('sum')) \
            .where(models.Book.id == id) \
            .join(models.Rate, models.Rate.fk_book == models.Book.id, isouter=True) \
            .group_by(models.Book).first()

        rating_new_format = []
        if data.count > 0:
            rates = self.session.query(models.Rate.text,
                                       models.Rate.formatted_date,
                                       models.Rate.likes,
                                       models.Rate.id,
                                       models.User.photo,
                                       models.Rate.rate,
                                       models.User.id.label('user_id'),
                                       models.User.nickname,
                                       models.Like.id.label('like_id'),
                                       func.count(models.Comment.id).label('comments')) \
                .where(models.Rate.fk_book == id) \
                .join(models.User, models.Rate.fk_user == models.User.id) \
                .join(models.Like, and_(models.Like.fk_rate == models.Rate.id,
                                        models.Like.fk_user == user_id,
                                        user_id is not None), isouter=True) \
                .join(models.Comment, models.Comment.fk_rate == models.Rate.id, isouter=True) \
                .group_by(models.Rate.text,
                          models.Rate.formatted_date,
                          models.Rate.likes,
                          models.Rate.id,
                          models.User.photo,
                          models.Rate.rate,
                          models.User.id.label('user_id'),
                          models.User.nickname,
                          models.Like.id.label('like_id')) \
                .offset(page * 20).limit(20).all()

            for rate in rates:
                rating_new_format.append({
                    'date': rate.formatted_date,
                    'id': rate.id,
                    'likes': rate.likes,
                    'rate': rate.rate,
                    'you_like': rate.like_id is not None,
                    'text': rate.text,
                    'comments': rate.comments,
                    'user': {
                        'nickname': rate.nickname,
                        'photo': rate.photo,
                        'id': rate.user_id
                    }
                })

        user = self.session.query(models.UserBook.fk_status) \
            .where(and_(models.UserBook.fk_book == id,
                        models.UserBook.fk_user == user_id)) \
            .first()

        people_reading = self.session.query(func.count(models.UserBook.fk_user).label('users')) \
            .where(models.UserBook.fk_status == ReadingTypes.READING).group_by(models.UserBook.fk_book).first()

        print(people_reading)

        book = get_by_identifier(data.identifier)

        if "volumeInfo" not in book:
            raise HTTPException(status_code=404, detail='Não encontrado')

        book = format_book_output(book)

        if isinstance(book, str):
            raise HTTPException(status_code=400, detail=book)

        book.update({
            'id': id,
            'status': user.fk_status if user else None,
            'rate': data.sum / data.count if data.count > 0 else None,
            'raters': data.count,
            'reviews': rating_new_format,
            'company': people_reading.users if people_reading else 0
        })

        return book

    def book_user_status(self, id_user: int, id_status: int, id_book: int):

        query = self.session.query(models.UserBook) \
            .where(and_(models.UserBook.fk_user == id_user, models.UserBook.fk_book == id_book)).first()

        # update
        if query:
            stmt = update(models.UserBook) \
                .where(and_(models.UserBook.fk_user == id_user,
                            models.UserBook.fk_book == id_book)) \
                .values(fk_book=id_book,
                        fk_user=id_user,
                        fk_status=id_status,
                        date=func.now()
                        )
            try:
                self.session.execute(stmt)
                self.session.commit()

                return {'id_book': id_book, 'id_status': id_status, 'id_user': id_user}
            except IntegrityError as err:
                self.session.rollback()
                print(err)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao adicionar um novo status.")
        # insert
        else:
            stmt = insert(models.UserBook).values(fk_book=id_book,
                                                  fk_user=id_user,
                                                  fk_status=id_status,
                                                  date=func.now()
                                                  )
            try:
                self.session.execute(stmt)
                self.session.commit()

                return {'id_book': id_book, 'id_status': id_status, 'id_user': id_user}
            except IntegrityError as err:
                self.session.rollback()
                print(err)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao adicionar um novo status.")

    def search_book(self, search: str, page: int):
        get_books = search_book(search, page, 16)
        aux = []
        for x in get_books['items']:
            book = format_book_output(x)
            
            query_book = self.session.query(models.Book.id.label('id'),
                                            func.count(models.Rate.id).label('count'),
                                            func.sum(models.Rate.rate).label('sum'))\
                                    .where(models.Book.identifier == book['identifier'])\
                                    .join(models.Rate, models.Rate.fk_book == models.Book.id)\
                                    .group_by(models.Book).first()
      
    
            aux.append({'id': query_book.id if query_book else None,
                        'rate': query_book.sum / query_book.count if query_book else 0,
                        'cover': book['cover'],
                        'identifier': book['identifier'],
                        'book_title': book['book_title'],
                        'author': book['author']
                    })
        return aux
    

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.db.models.models import *
from src.utils.format_book_output import get_and_format_output


class CrudComment:
    def __init__(self, session: Session):
        self.session = session

    def new_comment(self, data, user_id):
        stmt = Comment(fk_user=user_id, date=func.now(), text=data.text, likes=0, fk_rate=data.rate_id)
        self.session.add(stmt)
        self.session.commit()
        self.session.refresh(stmt)
        return {'comment_id': stmt.id}

    def get_comments(self, rate_id, user_id, page):
        review = self.session.query(Rate.id.label('rate_id'), Rate.text, Rate.rate, Rate.likes, Rate.formatted_date,
                                    Book.id.label('book_id'), Book.identifier,
                                    UserBook.fk_status.label('status'),
                                    Like.id.label('like_id'),
                                    User.id.label('user_id'), User.photo, User.nickname) \
            .where(Rate.id == rate_id) \
            .join(Book, Rate.fk_book == Book.id) \
            .join(User, User.id == Rate.fk_user) \
            .join(UserBook, and_(Book.id == UserBook.fk_book, UserBook.fk_user == user_id), isouter=True) \
            .join(Like, and_(Like.fk_user == user_id, Like.fk_rate == Rate.id), isouter=True).first()

        if not review:
            return None

        data = self.session.query(Comment.id.label('comment_id'), Comment.text, Comment.formatted_date, Comment.likes,
                                  User.id.label('user_id'), User.nickname, User.photo,
                                  Like.id.label('like_id')) \
            .where(Comment.fk_rate == rate_id) \
            .join(User, User.id == Comment.fk_user) \
            .join(Like, and_(Like.fk_user == user_id, Like.fk_comment == Comment.id), isouter=True) \
            .offset(page * 20).limit(20).all()

        def format_comment(comment):
            return {
                'id': comment['comment_id'],
                'likes': comment['likes'],
                'date': comment['formatted_date'],
                'text': comment['text'],
                'you_liked': True if comment['like_id'] else False,
                'user': {
                    'id': comment['user_id'],
                    'nickname': comment['nickname'],
                    'photo': comment['photo']
                }
            }

        comments = list(map(format_comment, data))
        book = get_and_format_output(review['identifier'])
        book.update({'id': review.book_id, 'status': review.status})

        return {
            'reviewer': {
                'id': review.user_id,
                'photo': review.photo,
                'nickname': review.nickname
            },
            'review': {
                'id': review.rate_id,
                'text': review.text,
                'rate': review.rate,
                'likes': review.likes,
                'date': review.formatted_date,
                'you_liked': True if review.like_id else False
            },
            'book': book,
            'comments': comments
        }

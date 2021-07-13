import sqlalchemy as sq
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = create_engine('sqlite:///tmp/expense.db',
                       connect_args={"check_same_thread": False},
                       pool_pre_ping=True)
DBSession = sessionmaker(bind=engine)
db = DBSession()

class Expense(Base):
    __tablename__ = 'expenses'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    pdf = sq.Column(sq.String, nullable=False, unique=True)
    txt = sq.Column(sq.Text)
    date = sq.Column(sq.String(10))
    amount = sq.Column(sq.Float)
    merchant=sq.Column(sq.String(20))
    category = sq.Column(sq.String(20), nullable=False)

    def save(self):
        db.add(self)
        db.commit()

        return self

    def delete(self):
        db.delete(self)
        return db.commit()

    @classmethod
    def get_all(cls, *order_by_args):
        if order_by_args:
            return db.query(cls,
            ).order_by(*order_by_args
            ).all()
        else:
            return db.query(cls
            ).all()

    @staticmethod
    def save_all(objs):
        db.add_all(objs)
        db.commit()


Base.metadata.create_all(engine)
from sqlalchemy import (Column, Integer, Sequence, UnicodeText)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Wisdom(Base):
    __tablename__ = 'wisdoms'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    text = Column(UnicodeText)

    def __repr__(self):
        return '<Wisdom("{}")>'.format(self.id)


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    title = Column(UnicodeText)

    def __repr__(self):
        return '<Chat("{}")>'.format(self.id)

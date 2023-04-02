from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Arts(Base):
    __tablename__ = 'arts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128))
    author = Column(String(64))
    filename = Column(String(128))
    sorting_id = Column(Integer, ForeignKey("sortings.id"))

    sorting = relationship("Sortings")


class Tags(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64))


class ArtTags(Base):
    __tablename__ = 'art_tags'

    id = Column(Integer, primary_key=True)
    art_id = Column(Integer, ForeignKey("arts.id", onupdate="CASCADE", ondelete="CASCADE"))
    tag_id = Column(Integer, ForeignKey("tags.id", onupdate="CASCADE", ondelete="CASCADE"))


class Sortings(Base):
    __tablename__ = 'sortings'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DATETIME)

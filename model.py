from sqlalchemy import Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, SmallInteger
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    candidates = relationship('Candidate', secondary='user_candidate')

class Candidate(Base):
    __tablename__ = 'candidate'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    screen_name = Column(String)
    photos = relationship('Photo', backref='candidate')
    users = relationship('User', secondary='user_candidate')

class Photo(Base):
    __tablename__ = 'photo'
    id = Column(String, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidate.id'))

class UserCandidate(Base):
    __tablename__ = 'user_candidate'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    candidate_id = Column(Integer, ForeignKey('candidate.id'))
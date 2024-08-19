from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    type = Column(Enum('account_leak', 'social_media', 'website', 'other', name='source_type'), nullable=False)
    name = Column(String, nullable=False)

class Entity(Base):
    __tablename__ = 'entities'
    id = Column(Integer, primary_key=True)
    type = Column(Enum('person', 'organization', 'location', 'other', name='entity_type'), nullable=False)
    name = Column(String, nullable=False)

class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('entities.id'))
    first_name = Column(String)
    last_name = Column(String)
    sex = Column(Enum('male', 'female', 'other', name='sex'))
    relationship_status = Column(Enum('single', 'married', 'divorced', 'widowed', 'separated', 'in_relationship', 'other', name='relationship_status'))

class EntityIdentifier(Base):
    __tablename__ = 'entity_identifiers'
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('entities.id'))
    identifier_type = Column(Enum('phone', 'email', 'username', 'tax_number', 'passport', 'national_id', 'other', name='identifier_type'), nullable=False)
    identifier_value = Column(String, nullable=False)

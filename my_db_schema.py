from sqlalchemy import create_engine
from sqlalchemy import Table, Column, String, Integer, MetaData, ForeignKey, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func, and_, or_, not_
from sqlalchemy.orm import sessionmaker
import conf


Base = declarative_base()
# db_string = "postgres://sellonl:clone!draw_depart@127.0.0.1/sellonl"
db_string = conf.PG_CONF
engine = create_engine(db_string)
conn = engine.connect()
meta = MetaData(engine)
session = sessionmaker()
session.configure(bind=engine)


class CustomersInfo(Base):
    __tablename__ = 'tbl_customers_info'
    customers_info_id = Column(Integer(), ForeignKey('tbl_customers.customers_id'), primary_key=True)
    customers_mixed_info = Column(String())


class Customers(Base):
    __tablename__ = 'tbl_customers'
    customers_id = Column(Integer(), primary_key=True)
    customers_login = Column(String(), unique=True)
    customers_firstname = Column(String())
    customers_lastname = Column(String())
    customers_email_address = Column(String(), unique=True)
    customers_telephone = Column(String())
    customers_account = Column(Float())

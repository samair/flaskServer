from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    email_id =  Column(String, nullable=False, unique=True)
    Name =  Column(String, nullable=False, unique=True)
    id = Column(Integer, primary_key=True)
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

class Vendor(Base):
    __tablename__ = "vendor"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False,unique=True)
    user_id=Column(Integer, ForeignKey("user.id"))
    user = relationship(User)
    @property
    def serialize(self):
        return {
            'name': self.name,
            'vendorID':self.id
        }

class Items(Base):
    __tablename__ = "items"

    name = Column(String, nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    stock = Column(Integer)
    vendor_id = Column(Integer, ForeignKey("vendor.id"))
    vendor = relationship(Vendor)
    @property
    def serialize(self):
        return {
            'name': self.name,
            'vendor_id': self.vendor_id,
            'description': self.description,
            'Product_id': self.id,
            'price': self.price,
            'stock': self.stock
        }


engine = create_engine("sqlite:///geekshack.db")

Base.metadata.create_all(engine)

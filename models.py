from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True)
    email = Column(String(50), unique=True) 
    password = Column(String(500))
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    orders = relationship('Order', back_populates='user')

    def __repr__(self):
        return f'<User {self.username}>'

class Order(Base):
    ORDER_STATUS = (
        ('PENDING', 'pending'),
        ('PROCESSING', 'processing'),
        ('DELIVERED', 'delivered'),
        ('CANCELED', 'canceled')
    )

    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer, nullable=False)
    order_status = Column(ChoiceType(ORDER_STATUS) , default='PENDING')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='orders')
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship('Product', back_populates='orders')
   

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)
    description = Column(Text)
    price = Column(Integer)
    quantity = Column(Integer)
    image = Column(String(255))
    orders = relationship('Order', back_populates='product')

    def __repr__(self):
        return f'<Product {self.name}>'
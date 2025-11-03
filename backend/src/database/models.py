"""
📄 models.py
Define os modelos de dados (ORM) usados pelo SQLAlchemy para mapear tabelas
do banco PostgreSQL.

👉 Padrão seguido:
- Código limpo e bem documentado
- Compatível com o SQLAlchemy 2.x
- Facilita consultas e agregações para o módulo analytics_service.py
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .session import Base


# 🧾 Modelo de Tabela: Restaurantes
class Restaurant(Base):
    """
    🍽️ Representa um restaurante cadastrado no sistema.
    """
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(150), nullable=True)

    # 🔗 Relacionamento com vendas
    sales = relationship("Sale", back_populates="restaurant")


# 💰 Modelo de Tabela: Vendas
class Sale(Base):
    """
    💵 Representa uma venda registrada (simulada ou real).
    """
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    product_name = Column(String(120), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    total_value = Column(Float, nullable=False)
    sale_channel = Column(String(50), nullable=False, default="Presencial")  # iFood, Rappi, etc.
    sale_date = Column(DateTime, default=datetime.utcnow)

    # 🔗 Relação reversa com restaurante
    restaurant = relationship("Restaurant", back_populates="sales")

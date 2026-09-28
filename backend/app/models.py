from sqlalchemy import Boolean, Column, Integer, String, Text

from .database import Base


class MachineField(Base):
    __tablename__ = "machine_fields"

    id = Column(Integer, primary_key=True, index=True)
    field_name = Column(String(100), nullable=False, unique=True)
    field_type = Column(String(20), nullable=False)
    required = Column(Boolean, default=False, nullable=False)
    dropdown_options = Column(Text, nullable=True)


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    field_values = Column(Text, nullable=False)
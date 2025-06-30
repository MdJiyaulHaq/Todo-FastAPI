from database import Base
from sqlalchemy import Column, Integer, String, Boolean


class Todo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    priority = Column(Integer, default=1)
    completed = Column(Boolean, default=False)

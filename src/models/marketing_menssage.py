from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ...config import Base

class MarketingMenssage(Base):
    __tablename__ = "marketing_menssages"

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    establishments_id = Column(Integer, ForeignKey("establishments.id", ondelete = "CASCADE", onupdate = "CASCADE"), nullable = False)
    title = Column(String(150), nullable = False)
    content = Column(Text, nullable = False)
    establishment = relationship("Establishment", backref = "marketing_menssages", foreign_keys = [establishments_id])

    def __repr__(self):
        return (
            f"<MarketingMenssage(id={self.id}, establishments_id={self.establishments_id}, "
            f"title='{self.title}', content='{self.content}')>"
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "establishments_id": self.establishments_id,
            "title": self.title,
            "content": self.content,
            "establishment": self.establishment.to_dict() if self.establishment else None
        }
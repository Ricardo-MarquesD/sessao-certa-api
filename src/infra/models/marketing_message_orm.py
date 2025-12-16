from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, validates
from config import Base

class MarketingMessageModel(Base):
    __tablename__ = "marketing_messages"

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    establishments_id = Column(Integer, ForeignKey("establishments.id", ondelete = "CASCADE", onupdate = "CASCADE"), nullable = False)
    title = Column(String(150), nullable = False)
    content = Column(Text, nullable = False)
    establishment = relationship("EstablishmentModel", backref = "marketing_messages", foreign_keys = [establishments_id])

    def __repr__(self):
        return (
            f"<MarketingMessage(id={self.id}, establishments_id={self.establishments_id}, "
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
    
    @validates('title')
    def validate_title(self, key, title_value):
        if not title_value:
            raise ValueError("Title cannot be empty")
        return title_value
    
    @validates('content')
    def validate_content(self, key, content_value):
        if not content_value:
            raise ValueError("Content cannot be empty")
        return content_value
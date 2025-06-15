from src.models.wardrobe import db  # 從 wardrobe 導入 db
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=True)
    style_level = db.Column(db.Integer, default=3)
    location = db.Column(db.String(100), default='台北市')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'style_level': self.style_level,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

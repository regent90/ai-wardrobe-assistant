from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class ClothingItem(db.Model):
    __tablename__ = 'clothing_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, default=1)  # 移除外鍵約束，暫時簡化
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    primary_color = db.Column(db.String(50), nullable=True)
    style = db.Column(db.String(50), nullable=True)
    material = db.Column(db.String(100), nullable=True)
    suitable_seasons = db.Column(db.Text, nullable=True)  # JSON string
    suitable_occasions = db.Column(db.Text, nullable=True)  # JSON string
    photo_path = db.Column(db.String(255), nullable=True)
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'category': self.category,
            'primary_color': self.primary_color,
            'style': self.style,
            'material': self.material,
            'suitable_seasons': json.loads(self.suitable_seasons) if self.suitable_seasons else [],
            'suitable_occasions': json.loads(self.suitable_occasions) if self.suitable_occasions else [],
            'photo_path': self.photo_path,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class FavoriteOutfit(db.Model):
    __tablename__ = 'favorite_outfits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, default=1)
    outfit_data = db.Column(db.Text, nullable=False)  # JSON string
    score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'outfit_data': self.outfit_data,
            'score': self.score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

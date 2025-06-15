import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app
from src.models.wardrobe import db
from src.models.user import User

def reset_database():
    with app.app_context():
        try:
            print("開始重建資料庫...")
            
            # 刪除所有表格
            db.drop_all()
            print("刪除所有表格")
            
            # 重新建立所有表格
            db.create_all()
            print("重新建立所有表格")
            
            # 建立預設用戶
            default_user = User(
                id=1,
                username='default_user',
                email='user@example.com',
                style_level=3,
                location='台北市'
            )
            db.session.add(default_user)
            db.session.commit()
            print("建立預設用戶 (ID: 1)")
            
            print("✅ 資料庫重建完成！")
            
        except Exception as e:
            print(f"❌ 錯誤: {e}")
            db.session.rollback()

if __name__ == '__main__':
    reset_database()

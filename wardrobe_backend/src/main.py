import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.wardrobe import db, ClothingItem, FavoriteOutfit  # 改為從 wardrobe 導入
from src.models.user import User  # 單獨導入 User 模型
from src.routes.user import user_bp
from src.routes.clothing import clothing_bp
from src.routes.recommendations import recommendations_bp
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# 啟用 CORS
CORS(app, origins="*")

# 資料庫配置
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 初始化資料庫
db.init_app(app)

# 註冊藍圖
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(clothing_bp, url_prefix='/api')
app.register_blueprint(recommendations_bp, url_prefix='/api')

# 建立資料庫表格和初始資料
with app.app_context():
    db.create_all()
    
    # 檢查是否有預設用戶，沒有則建立
    if not User.query.filter_by(id=1).first():
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

# 靜態檔案服務
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
    return send_from_directory(upload_folder, filename)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# 健康檢查端點
@app.route('/api/health')
def health_check():
    return {'status': 'healthy', 'message': 'AI Wardrobe Backend is running'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

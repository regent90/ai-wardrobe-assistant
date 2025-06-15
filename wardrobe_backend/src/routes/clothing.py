from flask import Blueprint, request, jsonify
from src.models.wardrobe import db, ClothingItem, FavoriteOutfit
from src.services.ai_service import AIService, OutfitScoringSystem
import os
import json
import uuid
from werkzeug.utils import secure_filename

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available. Image processing will be disabled.")

clothing_bp = Blueprint('clothing', __name__)

# 配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    upload_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), UPLOAD_FOLDER)
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    return upload_path

@clothing_bp.route('/clothing', methods=['GET'])
def get_clothing_items():
    """獲取所有衣物"""
    try:
        print("=== 開始獲取衣物資料 ===")  # 調試用
        user_id = request.args.get('user_id', 1)
        print(f"用戶ID: {user_id}")
        
        # 檢查資料庫連接
        items = ClothingItem.query.filter_by(user_id=user_id).all()
        print(f"找到 {len(items)} 件衣物")
        
        result = {
            'success': True,
            'data': [item.to_dict() for item in items]
        }
        print(f"回傳資料: {result}")
        return jsonify(result)
        
    except Exception as e:
        print(f"=== 錯誤發生 ===")
        print(f"錯誤類型: {type(e).__name__}")
        print(f"錯誤訊息: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@clothing_bp.route('/clothing', methods=['POST'])
def add_clothing_item():
    """新增衣物"""
    try:
        user_id = request.form.get('user_id', 1)
        
        # 處理圖片上傳
        photo_path = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                upload_path = ensure_upload_folder()
                filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                file_path = os.path.join(upload_path, filename)
                file.save(file_path)
                photo_path = f'/uploads/{filename}'
                
                # 如果有AI服務，進行圖片分析
                ai_api_key = os.getenv('GEMINI_API_KEY')
                if ai_api_key:
                    try:
                        ai_service = AIService(ai_api_key)
                        ai_result = ai_service.analyze_clothing_image(file_path)
                        
                        # 使用AI分析結果
                        item = ClothingItem(
                            user_id=user_id,
                            name=request.form.get('name', ai_result.get('name', '新衣物')),
                            category=request.form.get('category', ai_result.get('category', '其他')),
                            primary_color=request.form.get('primary_color', ai_result.get('primary_color', '')),
                            style=request.form.get('style', ai_result.get('style', '')),
                            material=request.form.get('material', ai_result.get('material', '')),
                            suitable_seasons=json.dumps(request.form.getlist("suitable_seasons") or ai_result.get("suitable_seasons", [])),
                            suitable_occasions=json.dumps(request.form.getlist("suitable_occasions") or ai_result.get("suitable_occasions", [])),
                            photo_path=photo_path
                        )
                    except Exception as ai_error:
                        print(f"AI分析失敗: {ai_error}")
                        # 使用手動輸入的資料
                        item = ClothingItem(
                            user_id=user_id,
                            name=request.form.get('name', '新衣物'),
                            category=request.form.get('category', '其他'),
                            primary_color=request.form.get('primary_color', ''),
                            style=request.form.get('style', ''),
                            material=request.form.get('material', ''),
                            suitable_seasons=json.dumps(request.form.getlist('suitable_seasons')),
                            suitable_occasions=json.dumps(request.form.getlist('suitable_occasions')),
                            photo_path=photo_path
                        )
                else:
                    # 沒有AI服務，使用手動輸入
                    item = ClothingItem(
                        user_id=user_id,
                        name=request.form.get('name', '新衣物'),
                        category=request.form.get('category', '其他'),
                        primary_color=request.form.get('primary_color', ''),
                        style=request.form.get('style', ''),
                        material=request.form.get('material', ''),
                        suitable_seasons=json.dumps(request.form.getlist('suitable_seasons')),
                        suitable_occasions=json.dumps(request.form.getlist('suitable_occasions')),
                        photo_path=photo_path
                    )
        else:
            # 沒有圖片，使用手動輸入
            item = ClothingItem(
                user_id=user_id,
                name=request.form.get('name', '新衣物'),
                category=request.form.get('category', '其他'),
                primary_color=request.form.get('primary_color', ''),
                style=request.form.get('style', ''),
                material=request.form.get('material', ''),
                suitable_seasons=json.dumps(request.form.getlist('suitable_seasons')),
                suitable_occasions=json.dumps(request.form.getlist('suitable_occasions')),
                photo_path=photo_path
            )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': item.to_dict(),
            'message': '衣物新增成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@clothing_bp.route('/clothing/<int:item_id>', methods=['PUT'])
def update_clothing_item(item_id):
    """更新衣物"""
    try:
        item = ClothingItem.query.get_or_404(item_id)
        
        data = request.get_json()
        if data.get('name'):
            item.name = data['name']
        if data.get('category'):
            item.category = data['category']
        if data.get('primary_color'):
            item.primary_color = data['primary_color']
        if data.get('style'):
            item.style = data['style']
        if data.get('material'):
            item.material = data['material']
        if data.get('suitable_seasons'):
            item.suitable_seasons = json.dumps(data['suitable_seasons'])
        if data.get('suitable_occasions'):
            item.suitable_occasions = json.dumps(data['suitable_occasions'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': item.to_dict(),
            'message': '衣物更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@clothing_bp.route('/clothing/<int:item_id>', methods=['DELETE'])
def delete_clothing_item(item_id):
    """刪除衣物"""
    try:
        item = ClothingItem.query.get_or_404(item_id)
        
        # 刪除圖片檔案
        if item.photo_path:
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), item.photo_path.lstrip('/'))
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '衣物刪除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@clothing_bp.route('/clothing/analyze', methods=['POST'])
def analyze_clothing():
    """AI 分析衣物圖片"""
    try:
        if 'photo' not in request.files:
            return jsonify({'success': False, 'error': '沒有上傳圖片'}), 400
        
        file = request.files['photo']
        if not file or not file.filename or not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '無效的圖片檔案'}), 400
        
        # 儲存臨時檔案
        upload_path = ensure_upload_folder()
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        
        # AI 分析
        ai_api_key = os.getenv('GEMINI_API_KEY')
        if not ai_api_key:
            return jsonify({'success': False, 'error': 'AI服務未配置'}), 500
        
        ai_service = AIService(ai_api_key)
        result = ai_service.analyze_clothing_image(file_path)
        
        # 清理臨時檔案
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


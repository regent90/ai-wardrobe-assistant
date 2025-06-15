from flask import Blueprint, request, jsonify
from src.models.wardrobe import db, ClothingItem, FavoriteOutfit
from src.services.ai_service import WeatherService, OutfitScoringSystem
import os
import json
import random
from itertools import combinations

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/weather/<city>', methods=['GET'])
def get_weather(city):
    """獲取天氣資訊"""
    try:
        weather_api_key = os.getenv("WEATHER_API_KEY")
        weather_service = WeatherService(weather_api_key)
        weather_data = weather_service.get_weather_by_city(city)
        
        return jsonify({
            'success': True,
            'data': weather_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@recommendations_bp.route('/recommendations/generate', methods=['POST'])
def generate_recommendations():
    """生成穿搭推薦"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        weather = data.get('weather', {})
        occasion = data.get('occasion', '日常')
        style_level = data.get('style_level', 3)
        
        # 獲取用戶所有衣物
        all_items = ClothingItem.query.filter_by(user_id=user_id).all()
        if len(all_items) < 2:
            return jsonify({
                'success': True,
                'data': [],
                'message': '衣櫃中的衣物不足，無法生成推薦'
            })
        
        # 轉換為字典格式
        items_dict = [item.to_dict() for item in all_items]
        
        # 根據溫度確定季節
        temperature = weather.get('temperature', 20)
        if temperature < 15:
            season = '冬季'
        elif temperature < 20:
            season = '秋季'
        elif temperature < 25:
            season = '春季'
        else:
            season = '夏季'
        
        # 篩選適合的衣物
        suitable_items = filter_items_by_criteria(items_dict, season, occasion, style_level)
        
        if len(suitable_items) < 2:
            return jsonify({
                'success': True,
                'data': [],
                'message': f'找不到適合{season}和{occasion}場合的衣物組合'
            })
        
        # 按類別分組
        items_by_category = {}
        for item in suitable_items:
            category = item.get('category', '其他')
            items_by_category.setdefault(category, []).append(item)
        
        # 生成搭配組合
        outfit_combinations = generate_outfit_combinations(items_by_category, temperature)
        
        if not outfit_combinations:
            return jsonify({
                'success': True,
                'data': [],
                'message': '無法生成適合的搭配組合'
            })
        
        # 使用AI評分系統評分
        scoring_system = OutfitScoringSystem()
        scored_outfits = []
        
        for outfit_items in outfit_combinations:
            score = scoring_system.calculate_outfit_score(outfit_items, weather, occasion, style_level)
            
            explanation = create_outfit_explanation(outfit_items, weather, score, style_level)
            
            scored_outfits.append({
                'id': f"outfit_{random.randint(1000, 9999)}",
                'items': outfit_items,
                'score': score,
                'explanation': explanation
            })
        
        # 排序並選擇最佳推薦
        best_outfits = sorted(scored_outfits, key=lambda x: x['score'], reverse=True)[:3]
        final_recommendations = [outfit for outfit in best_outfits if outfit['score'] >= 60]
        
        return jsonify({
            'success': True,
            'data': final_recommendations
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@recommendations_bp.route('/outfits/favorite', methods=['POST'])
def save_favorite_outfit():
    """收藏穿搭"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        outfit_data = data.get('outfit_data')
        score = data.get('score', 0)
        
        favorite = FavoriteOutfit(
            user_id=user_id,
            outfit_data=json.dumps(outfit_data),
            score=score
        )
        
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': favorite.to_dict(),
            'message': '穿搭收藏成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@recommendations_bp.route('/outfits/favorites', methods=['GET'])
def get_favorite_outfits():
    """獲取收藏的穿搭"""
    try:
        user_id = request.args.get('user_id', 1)
        favorites = FavoriteOutfit.query.filter_by(user_id=user_id).order_by(FavoriteOutfit.created_at.desc()).all()
        
        result = []
        for favorite in favorites:
            favorite_dict = favorite.to_dict()
            try:
                favorite_dict['outfit_data'] = json.loads(favorite_dict['outfit_data'])
            except:
                pass
            result.append(favorite_dict)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@recommendations_bp.route('/outfits/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite_outfit(favorite_id):
    """刪除收藏的穿搭"""
    try:
        favorite = FavoriteOutfit.query.get_or_404(favorite_id)
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '收藏刪除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@recommendations_bp.route('/stats/wardrobe', methods=['GET'])
def get_wardrobe_stats():
    """獲取衣櫃統計數據"""
    try:
        user_id = request.args.get('user_id', 1)
        items = ClothingItem.query.filter_by(user_id=user_id).all()
        
        # 統計數據
        total_items = len(items)
        avg_usage = sum(item.usage_count for item in items) / total_items if total_items > 0 else 0
        
        # 按類別統計
        category_stats = {}
        color_stats = {}
        style_stats = {}
        
        for item in items:
            # 類別統計
            category = item.category or '其他'
            category_stats[category] = category_stats.get(category, 0) + 1
            
            # 顏色統計
            color = item.primary_color or '未知'
            color_stats[color] = color_stats.get(color, 0) + 1
            
            # 風格統計
            style = item.style or '未知'
            style_stats[style] = style_stats.get(style, 0) + 1
        
        # 最常穿的衣物
        most_worn = sorted(items, key=lambda x: x.usage_count, reverse=True)[:5]
        
        return jsonify({
            'success': True,
            'data': {
                'total_items': total_items,
                'average_usage': round(avg_usage, 1),
                'category_distribution': category_stats,
                'color_distribution': color_stats,
                'style_distribution': style_stats,
                'most_worn_items': [item.to_dict() for item in most_worn]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def filter_items_by_criteria(all_items, season, occasion, style_level):
    """根據條件篩選衣物"""
    scoring_system = OutfitScoringSystem()
    style_prefs = scoring_system.style_level_preferences[style_level]
    preferred_colors = style_prefs['colors']
    preferred_styles = style_prefs['styles']
    
    suitable_items = []
    for item in all_items:
        # 季節篩選
        seasons = item.get('suitable_seasons', [])
        if isinstance(seasons, str):
            try:
                seasons = json.loads(seasons)
            except:
                seasons = [s.strip() for s in seasons.split(',') if s.strip()]
        season_match = not seasons or season in seasons
        
        # 場合篩選
        occasions = item.get('suitable_occasions', [])
        if isinstance(occasions, str):
            try:
                occasions = json.loads(occasions)
            except:
                occasions = [o.strip() for o in occasions.split(',') if o.strip()]
        occasion_match = not occasions or occasion in occasions
        
        # 風格篩選
        item_style = item.get('style', '')
        style_match = item_style in preferred_styles
        
        # 顏色偏好篩選
        item_color = item.get('primary_color', '')
        color_preference = item_color in preferred_colors or style_level == 3
        
        if season_match and occasion_match and (style_match or color_preference):
            suitable_items.append(item)
    
    return suitable_items

def generate_outfit_combinations(items_by_category, temperature):
    """生成穿搭組合"""
    combinations_list = []
    
    tops = items_by_category.get('上衣', [])
    bottoms = items_by_category.get('下著', [])
    outerwears = items_by_category.get('外套', [])
    shoes = items_by_category.get('鞋子', [])
    
    # 基礎搭配（上衣+下著）
    for top in tops[:3]:  # 限制數量以提高性能
        for bottom in bottoms[:3]:
            combo = [top, bottom]
            if shoes:
                combo.append(shoes[0])
            combinations_list.append(combo)
    
    # 層次搭配（當溫度較低時加入外套）
    if temperature < 22 and outerwears:
        for top in tops[:2]:
            for bottom in bottoms[:2]:
                for outer in outerwears[:2]:
                    combo = [top, bottom, outer]
                    if shoes:
                        combo.append(shoes[0])
                    combinations_list.append(combo)
    
    return combinations_list[:10]  # 限制組合數量

def create_outfit_explanation(outfit_items, weather, score, style_level):
    """生成穿搭說明"""
    style_names = {1: "保守經典", 2: "簡約實用", 3: "日常時尚", 4: "潮流前衛", 5: "大膽創新"}
    
    # 提取衣物資訊
    top = next((item for item in outfit_items if item['category'] == '上衣'), None)
    bottom = next((item for item in outfit_items if item['category'] == '下著'), None)
    outerwear = next((item for item in outfit_items if item['category'] == '外套'), None)
    
    score_level = "優秀" if score >= 80 else "良好" if score >= 70 else "及格" if score >= 60 else "需改進"
    
    # 搭配亮點分析
    highlights = []
    
    # 顏色分析
    if top and bottom:
        top_color = top.get('primary_color', '')
        bottom_color = bottom.get('primary_color', '')
        if top_color == bottom_color:
            highlights.append(f"**同色系搭配**：{top_color}單色調營造簡潔統一感")
        else:
            highlights.append(f"**經典配色**：{top_color}與{bottom_color}的搭配既和諧又有層次")
    
    # 風格分析
    styles = {item.get('style', '') for item in outfit_items if item.get('style')}
    if len(styles) == 1:
        highlights.append(f"**風格統一**：全套{list(styles)[0]}風格，符合您的{style_names[style_level]}偏好")
    
    # 天氣適應性
    temp = weather.get('temperature', 20)
    if outerwear:
        highlights.append(f"**溫度適應**：{temp}°C的天氣搭配外套，實用又時尚")
    elif temp > 25:
        highlights.append(f"**清爽搭配**：適合{temp}°C的輕鬆穿搭")
    
    explanation = f"""
💡 **AI穿搭分析** (評分: {score:.1f}/100 - {score_level})

{chr(10).join(['- ' + highlight for highlight in highlights[:3]])}

🎯 **推薦理由**: 這套搭配根據您的{style_names[style_level]}風格偏好量身定制，在色彩和諧度、風格一致性和天氣適應性方面都有優異表現。
"""
    
    return explanation.strip()


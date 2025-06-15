import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests

try:
    import google.generativeai as genai
    from PIL import Image
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: Google Generative AI not available. AI features will be disabled.")

class AIService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        if GEMINI_AVAILABLE:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None
    
    def analyze_clothing_image(self, image_path: str) -> Dict[str, Any]:
        """分析衣物圖片並返回結構化資訊"""
        if not GEMINI_AVAILABLE or not self.model:
            return self._get_default_analysis()
            
        try:
            image = Image.open(image_path)
            
            prompt = """
            請分析這張衣物圖片，並以JSON格式返回以下資訊：
            {
                "name": "衣物名稱",
                "category": "類別（上衣/下著/外套/鞋子/配件）",
                "primary_color": "主要顏色",
                "style": "風格（正式/休閒/運動/浪漫/復古/現代）",
                "material": "材質描述",
                "suitable_seasons": ["適合季節"],
                "suitable_occasions": ["適合場合"],
                "confidence": 0.95
            }
            
            請確保返回有效的JSON格式，不要包含其他文字。
            """
            
            response = self.model.generate_content([prompt, image])
            
            # 解析回應
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            result = json.loads(response_text)
            return result
            
        except Exception as e:
            print(f"AI分析錯誤: {e}")
            return self._get_default_analysis()
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """返回預設分析結果"""
        return {
            "name": "未知衣物",
            "category": "其他",
            "primary_color": "未知",
            "style": "休閒",
            "material": "未知",
            "suitable_seasons": ["春季", "夏季", "秋季", "冬季"],
            "suitable_occasions": ["日常"],
            "confidence": 0.0
        }

class WeatherService:
    """OpenWeather One Call API 3.0 天氣服務"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required for WeatherService.")
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/3.0/onecall"
        self.geo_url = "https://api.openweathermap.org/geo/1.0"
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
        # 台灣主要城市映射
        self.taiwan_cities = {
            '台北': 'Taipei', '台北市': 'Taipei', '新北': 'New Taipei', '新北市': 'New Taipei',
            '桃園': 'Taoyuan', '台中': 'Taichung', '台中市': 'Taichung', '台南': 'Tainan',
            '台南市': 'Tainan', '高雄': 'Kaohsiung', '高雄市': 'Kaohsiung', '基隆': 'Keelung',
            '新竹': 'Hsinchu', '嘉義': 'Chiayi', '宜蘭': 'Yilan', '花蓮': 'Hualien', '台東': 'Taitung'
        }

    def _get_coordinates(self, city_name: str) -> Optional[Dict[str, float]]:
        params = {'q': f"{city_name},TW", 'limit': 1, 'appid': self.api_key}
        try:
            response = self.session.get(f"{self.geo_url}/direct", params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data:
                return {'lat': data[0]['lat'], 'lon': data[0]['lon']}
            self.logger.warning(f"找不到城市 {city_name} 的座標。")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"獲取座標失敗 for city {city_name}: {e}")
            return None

    def get_weather_by_city(self, city_name: str) -> Optional[Dict[str, Any]]:
        english_city = self.taiwan_cities.get(city_name, city_name)
        coordinates = self._get_coordinates(english_city)
        if not coordinates:
            return None
        
        weather_data = self._get_onecall_weather(coordinates['lat'], coordinates['lon'])
        return self._process_onecall_data(weather_data, city_name) if weather_data else None

    def _get_onecall_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        params = {
            'lat': lat, 'lon': lon, 'appid': self.api_key,
            'units': 'metric', 'lang': 'zh_tw', 'exclude': 'minutely,alerts'
        }
        try:
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"One Call API請求失敗 for lat={lat}, lon={lon}: {e}")
            return None

    def _process_onecall_data(self, data: Dict[str, Any], city_name: str) -> Dict[str, Any]:
        """處理One Call API返回數據"""
        current = data.get('current', {})
        weather = current.get('weather', [{}])[0] if current.get('weather') else {}
        
        return {
            'city_name': city_name,
            'temperature': round(current.get('temp', 0)),
            'feels_like': round(current.get('feels_like', 0)),
            'humidity': current.get('humidity', 0),
            'pressure': current.get('pressure', 1013),
            'wind_speed': current.get('wind_speed', 0),
            'wind_deg': current.get('wind_deg', 0),
            'cloudiness': current.get('clouds', 0),
            'weather_main': weather.get('main', 'Clear'),
            'weather_description': weather.get('description', '晴朗'),
            'weather_icon': weather.get('icon', '01d'),
            'sunrise': current.get('sunrise', 0),
            'sunset': current.get('sunset', 0),
            'timestamp': datetime.now().isoformat()
        }

    def extract_outfit_relevant_data(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取與穿搭相關的天氣數據"""
        if not weather_data:
            return self._get_default_outfit_data()
        
        temp = weather_data.get('temperature', 20)
        humidity = weather_data.get('humidity', 50)
        wind_speed = weather_data.get('wind_speed', 0)
        weather_main = weather_data.get('weather_main', 'Clear')
        
        return {
            'temperature': temp,
            'feels_like': weather_data.get('feels_like', temp),
            'humidity': humidity,
            'wind_speed': wind_speed,
            'weather_main': weather_main,
            'weather_description': weather_data.get('weather_description', '晴朗'),
            'weather_icon': weather_data.get('weather_icon', '01d'),
            'temperature_category': self._categorize_temperature(temp),
            'weather_condition': self._categorize_weather(weather_main),
            'clothing_suggestions': self._generate_clothing_suggestions(temp, humidity, wind_speed, weather_main),
            'comfort_level': self._calculate_comfort_level(temp, humidity, wind_speed)
        }

    def _categorize_temperature(self, temp: float) -> str:
        """分類溫度"""
        if temp < 10:
            return "寒冷"
        elif temp < 18:
            return "涼爽"
        elif temp < 26:
            return "舒適"
        elif temp < 32:
            return "溫暖"
        else:
            return "炎熱"

    def _categorize_weather(self, weather_main: str) -> str:
        """分類天氣狀況"""
        weather_map = {
            'Clear': '晴朗',
            'Clouds': '多雲',
            'Rain': '雨天',
            'Snow': '下雪',
            'Thunderstorm': '雷雨',
            'Drizzle': '小雨',
            'Mist': '薄霧',
            'Fog': '濃霧'
        }
        return weather_map.get(weather_main, '未知')

    def _generate_clothing_suggestions(self, temp: float, humidity: int, wind_speed: float, weather_main: str) -> Dict[str, List[str]]:
        """生成服裝建議"""
        suggestions = {
            '上衣': [],
            '下著': [],
            '外套': [],
            '鞋子': [],
            '配件': []
        }
        
        # 基於溫度的建議
        if temp < 10:
            suggestions['上衣'].extend(['厚毛衣', '保暖內衣', '長袖襯衫'])
            suggestions['下著'].extend(['厚褲子', '保暖褲', '牛仔褲'])
            suggestions['外套'].extend(['羽絨外套', '厚大衣', '防風外套'])
            suggestions['配件'].extend(['圍巾', '手套', '毛帽'])
        elif temp < 18:
            suggestions['上衣'].extend(['薄毛衣', '長袖上衣', '襯衫'])
            suggestions['下著'].extend(['長褲', '牛仔褲'])
            suggestions['外套'].extend(['薄外套', '開襟衫'])
        elif temp < 26:
            suggestions['上衣'].extend(['長袖上衣', '薄襯衫', 'T恤'])
            suggestions['下著'].extend(['長褲', '九分褲', '薄褲'])
        else:
            suggestions['上衣'].extend(['短袖上衣', 'T恤', '背心'])
            suggestions['下著'].extend(['短褲', '短裙', '薄褲'])
        
        # 基於天氣的建議
        if weather_main in ['Rain', 'Thunderstorm', 'Drizzle']:
            suggestions['外套'].append('雨衣')
            suggestions['鞋子'].extend(['雨鞋', '防水鞋'])
            suggestions['配件'].append('雨傘')
        
        if wind_speed > 5:
            suggestions['外套'].append('防風外套')
        
        if humidity > 80:
            suggestions['上衣'].append('透氣材質')
            
        return suggestions

    def _calculate_comfort_level(self, temp: float, humidity: int, wind_speed: float) -> str:
        """計算舒適度等級"""
        # 簡化的舒適度計算
        comfort_score = 0
        
        # 溫度舒適度 (18-26°C 最舒適)
        if 18 <= temp <= 26:
            comfort_score += 40
        elif 15 <= temp <= 30:
            comfort_score += 30
        else:
            comfort_score += 10
        
        # 濕度舒適度 (40-60% 最舒適)
        if 40 <= humidity <= 60:
            comfort_score += 30
        elif 30 <= humidity <= 70:
            comfort_score += 20
        else:
            comfort_score += 10
        
        # 風速舒適度
        if wind_speed <= 3:
            comfort_score += 30
        elif wind_speed <= 7:
            comfort_score += 20
        else:
            comfort_score += 10
        
        if comfort_score >= 80:
            return "非常舒適"
        elif comfort_score >= 60:
            return "舒適"
        elif comfort_score >= 40:
            return "一般"
        else:
            return "不舒適"

    def _get_default_outfit_data(self) -> Dict[str, Any]:
        """獲取預設穿搭數據"""
        return {
            'temperature': 22,
            'feels_like': 22,
            'humidity': 60,
            'wind_speed': 2.5,
            'weather_main': 'Clear',
            'weather_description': '晴朗',
            'weather_icon': '01d',
            'temperature_category': '舒適',
            'weather_condition': '晴朗',
            'clothing_suggestions': {
                '上衣': ['T恤', '襯衫'],
                '下著': ['長褲', '九分褲'],
                '外套': [],
                '鞋子': ['休閒鞋'],
                '配件': []
            },
            'comfort_level': '舒適'
        }

    def _get_mock_weather(self, city_name: str) -> Dict[str, Any]:
        """返回模擬天氣資料"""
        return {
            'city_name': city_name,
            'temperature': 27,
            'feels_like': 29,
            'humidity': 65,
            'pressure': 1013,
            'wind_speed': 1.03,
            'wind_deg': 180,
            'cloudiness': 40,
            'weather_main': 'Clouds',
            'weather_description': '多雲',
            'weather_icon': '02d',
            'sunrise': 1640995200,
            'sunset': 1641031200,
            'timestamp': datetime.now().isoformat()
        }

class OutfitScoringSystem:
    """穿搭評分系統"""
    
    def __init__(self):
        # 顏色相容性矩陣 - 擴展更多顏色變體
        self.color_compatibility = {
            # 基礎黑色系
            '黑色': ['白色', '灰色', '紅色', '藍色', '黃色', '綠色', '米色', '銀色'],
            '黑': ['白色', '灰色', '紅色', '藍色', '黃色', '綠色', '米色', '銀色'],
            'black': ['白色', '灰色', '紅色', '藍色', '黃色', '綠色', '米色', '銀色'],
            '深黑': ['白色', '灰色', '紅色', '藍色', '黃色', '綠色', '米色', '銀色'],
            
            # 基礎白色系
            '白色': ['黑色', '灰色', '藍色', '紅色', '綠色', '紫色', '粉色', '米色'],
            '白': ['黑色', '灰色', '藍色', '紅色', '綠色', '紫色', '粉色', '米色'],
            'white': ['黑色', '灰色', '藍色', '紅色', '綠色', '紫色', '粉色', '米色'],
            '純白': ['黑色', '灰色', '藍色', '紅色', '綠色', '紫色', '粉色', '米色'],
            '米白': ['黑色', '灰色', '藍色', '紅色', '綠色', '紫色', '粉色', '米色'],
            
            # 基礎灰色系
            '灰色': ['黑色', '白色', '藍色', '紅色', '黃色', '綠色', '紫色'],
            '灰': ['黑色', '白色', '藍色', '紅色', '黃色', '綠色', '紫色'],
            'gray': ['黑色', '白色', '藍色', '紅色', '黃色', '綠色', '紫色'],
            'grey': ['黑色', '白色', '藍色', '紅色', '黃色', '綠色', '紫色'],
            '深灰': ['黑色', '白色', '藍色', '紅色', '黃色', '綠色', '紫色'],
            '淺灰': ['黑色', '白色', '藍色', '紅色', '黃色', '綠色', '紫色'],
            '炭灰': ['黑色', '白色', '藍色', '紅色', '黃色', '綠色', '紫色'],
            
            # 基礎藍色系
            '藍色': ['白色', '黑色', '灰色', '米色', '棕色', '黃色', '綠色'],
            '藍': ['白色', '黑色', '灰色', '米色', '棕色', '黃色', '綠色'],
            'blue': ['白色', '黑色', '灰色', '米色', '棕色', '黃色', '綠色'],
            '深藍': ['白色', '黑色', '灰色', '米色', '棕色', '黃色', '綠色'],
            '淺藍': ['白色', '黑色', '灰色', '米色', '棕色', '黃色', '綠色'],
            '海軍藍': ['白色', '黑色', '灰色', '米色', '棕色', '黃色', '綠色'],
            '天藍': ['白色', '黑色', '灰色', '米色', '棕色', '黃色', '綠色'],
            '牛仔藍': ['白色', '黑色', '灰色', '米色', '棕色', '黃色', '綠色'],
            
            # 基礎紅色系
            '紅色': ['黑色', '白色', '灰色', '米色', '藍色'],
            '紅': ['黑色', '白色', '灰色', '米色', '藍色'],
            'red': ['黑色', '白色', '灰色', '米色', '藍色'],
            '深紅': ['黑色', '白色', '灰色', '米色', '藍色'],
            '酒紅': ['黑色', '白色', '灰色', '米色', '藍色'],
            '粉紅': ['白色', '黑色', '灰色', '米色'],
            '粉色': ['白色', '黑色', '灰色', '米色'],
            
            # 基礎綠色系
            '綠色': ['白色', '黑色', '米色', '棕色', '藍色', '灰色'],
            '綠': ['白色', '黑色', '米色', '棕色', '藍色', '灰色'],
            'green': ['白色', '黑色', '米色', '棕色', '藍色', '灰色'],
            '深綠': ['白色', '黑色', '米色', '棕色', '藍色', '灰色'],
            '淺綠': ['白色', '黑色', '米色', '棕色', '藍色', '灰色'],
            '軍綠': ['白色', '黑色', '米色', '棕色', '藍色', '灰色'],
            '橄欖綠': ['白色', '黑色', '米色', '棕色', '藍色', '灰色'],
            
            # 基礎黃色系
            '黃色': ['黑色', '灰色', '藍色', '白色', '棕色'],
            '黃': ['黑色', '灰色', '藍色', '白色', '棕色'],
            'yellow': ['黑色', '灰色', '藍色', '白色', '棕色'],
            '淺黃': ['黑色', '灰色', '藍色', '白色', '棕色'],
            '檸檬黃': ['黑色', '灰色', '藍色', '白色', '棕色'],
            
            # 基礎紫色系
            '紫色': ['白色', '黑色', '灰色', '銀色'],
            '紫': ['白色', '黑色', '灰色', '銀色'],
            'purple': ['白色', '黑色', '灰色', '銀色'],
            '深紫': ['白色', '黑色', '灰色', '銀色'],
            '淺紫': ['白色', '黑色', '灰色', '銀色'],
            
            # 基礎米色/棕色系
            '米色': ['藍色', '綠色', '棕色', '白色', '黑色', '灰色'],
            '米': ['藍色', '綠色', '棕色', '白色', '黑色', '灰色'],
            'beige': ['藍色', '綠色', '棕色', '白色', '黑色', '灰色'],
            '卡其': ['藍色', '綠色', '棕色', '白色', '黑色', '灰色'],
            '駝色': ['藍色', '綠色', '棕色', '白色', '黑色', '灰色'],
            
            '棕色': ['米色', '綠色', '藍色', '白色', '黑色', '灰色'],
            '棕': ['米色', '綠色', '藍色', '白色', '黑色', '灰色'],
            'brown': ['米色', '綠色', '藍色', '白色', '黑色', '灰色'],
            '咖啡色': ['米色', '綠色', '藍色', '白色', '黑色', '灰色'],
            '深棕': ['米色', '綠色', '藍色', '白色', '黑色', '灰色'],
            
            # 其他常見顏色
            '橙色': ['黑色', '白色', '灰色', '藍色', '棕色'],
            '橘色': ['黑色', '白色', '灰色', '藍色', '棕色'],
            'orange': ['黑色', '白色', '灰色', '藍色', '棕色'],
            
            '銀色': ['黑色', '白色', '灰色', '藍色', '紫色'],
            '銀': ['黑色', '白色', '灰色', '藍色', '紫色'],
            'silver': ['黑色', '白色', '灰色', '藍色', '紫色'],
            
            '金色': ['黑色', '白色', '棕色', '米色'],
            '金': ['黑色', '白色', '棕色', '米色'],
            'gold': ['黑色', '白色', '棕色', '米色'],
        }
        
        # 顏色分類映射 - 將相似顏色歸類
        self.color_categories = {
            '黑色系': ['黑色', '黑', 'black', '深黑', '炭黑'],
            '白色系': ['白色', '白', 'white', '純白', '米白', '象牙白'],
            '灰色系': ['灰色', '灰', 'gray', 'grey', '深灰', '淺灰', '炭灰', '銀灰'],
            '藍色系': ['藍色', '藍', 'blue', '深藍', '淺藍', '海軍藍', '天藍', '牛仔藍', '寶藍'],
            '紅色系': ['紅色', '紅', 'red', '深紅', '酒紅', '粉紅', '粉色', '桃紅'],
            '綠色系': ['綠色', '綠', 'green', '深綠', '淺綠', '軍綠', '橄欖綠', '草綠'],
            '黃色系': ['黃色', '黃', 'yellow', '淺黃', '檸檬黃', '金黃'],
            '紫色系': ['紫色', '紫', 'purple', '深紫', '淺紫', '薰衣草紫'],
            '棕色系': ['棕色', '棕', 'brown', '咖啡色', '深棕', '淺棕', '巧克力色'],
            '米色系': ['米色', '米', 'beige', '卡其', '駝色', '奶油色'],
            '橙色系': ['橙色', '橘色', 'orange', '橘紅', '橙黃'],
        }
        
        # 風格等級偏好
        self.style_level_preferences = {
            1: {'colors': ['黑色系', '白色系', '灰色系', '米色系'], 'styles': ['正式', '現代']},
            2: {'colors': ['黑色系', '白色系', '灰色系', '藍色系'], 'styles': ['休閒', '現代']},
            3: {'colors': ['黑色系', '白色系', '灰色系', '藍色系', '米色系'], 'styles': ['休閒', '現代', '正式']},
            4: {'colors': ['紅色系', '藍色系', '綠色系', '黃色系', '紫色系'], 'styles': ['現代', '浪漫']},
            5: {'colors': ['紅色系', '黃色系', '紫色系', '綠色系', '橙色系'], 'styles': ['浪漫', '復古']}
        }
    
    def _normalize_color(self, color: str) -> str:
        """標準化顏色名稱，返回顏色系別"""
        if not color:
            return '未知'
        
        color = color.strip().lower()
        
        # 直接查找顏色系別
        for category, colors in self.color_categories.items():
            if any(c.lower() in color or color in c.lower() for c in colors):
                return category
        
        # 模糊匹配常見顏色關鍵字
        color_keywords = {
            '黑': '黑色系', '白': '白色系', '灰': '灰色系', '藍': '藍色系',
            '紅': '紅色系', '綠': '綠色系', '黃': '黃色系', '紫': '紫色系',
            '棕': '棕色系', '米': '米色系', '橙': '橙色系', '橘': '橙色系',
            'black': '黑色系', 'white': '白色系', 'gray': '灰色系', 'grey': '灰色系',
            'blue': '藍色系', 'red': '紅色系', 'green': '綠色系', 'yellow': '黃色系',
            'purple': '紫色系', 'brown': '棕色系', 'beige': '米色系', 'orange': '橙色系'
        }
        
        for keyword, category in color_keywords.items():
            if keyword in color:
                return category
        
        return '其他'
    
    def _get_color_compatibility_score(self, color1: str, color2: str) -> float:
        """計算兩個顏色的相容性分數"""
        if not color1 or not color2:
            return 50
        
        # 標準化顏色
        norm_color1 = self._normalize_color(color1)
        norm_color2 = self._normalize_color(color2)
        
        # 同色系給高分
        if norm_color1 == norm_color2:
            return 85
        
        # 檢查經典搭配
        classic_combinations = [
            ('黑色系', '白色系'), ('白色系', '黑色系'),
            ('黑色系', '灰色系'), ('灰色系', '黑色系'),
            ('白色系', '灰色系'), ('灰色系', '白色系'),
            ('藍色系', '白色系'), ('白色系', '藍色系'),
            ('藍色系', '米色系'), ('米色系', '藍色系'),
            ('黑色系', '藍色系'), ('藍色系', '黑色系'),
            ('綠色系', '米色系'), ('米色系', '綠色系'),
            ('棕色系', '米色系'), ('米色系', '棕色系'),
        ]
        
        if (norm_color1, norm_color2) in classic_combinations:
            return 90
        
        # 中性色與其他顏色的搭配
        neutral_colors = ['黑色系', '白色系', '灰色系', '米色系']
        if norm_color1 in neutral_colors or norm_color2 in neutral_colors:
            return 75
        
        # 對比色搭配
        contrast_pairs = [
            ('紅色系', '綠色系'), ('綠色系', '紅色系'),
            ('藍色系', '橙色系'), ('橙色系', '藍色系'),
            ('黃色系', '紫色系'), ('紫色系', '黃色系'),
        ]
        
        if (norm_color1, norm_color2) in contrast_pairs:
            return 70
        
        # 相鄰色搭配
        adjacent_pairs = [
            ('藍色系', '綠色系'), ('綠色系', '藍色系'),
            ('紅色系', '橙色系'), ('橙色系', '紅色系'),
            ('黃色系', '橙色系'), ('橙色系', '黃色系'),
        ]
        
        if (norm_color1, norm_color2) in adjacent_pairs:
            return 80
        
        # 其他情況給予基礎分數
        return 60
    
    def calculate_outfit_score(self, outfit_items: List[Dict], weather: Dict, occasion: str, style_level: int) -> float:
        """計算穿搭總分（0-100分）"""
        if len(outfit_items) < 2:
            return 0
        
        # 顏色搭配評分 (30%)
        color_score = self._calculate_color_harmony(outfit_items)
        
        # 風格一致性評分 (25%)
        style_score = self._calculate_style_consistency(outfit_items, style_level)
        
        # 天氣適應性評分 (25%)
        weather_score = self._calculate_weather_appropriateness(outfit_items, weather)
        
        # 場合適用性評分 (20%)
        occasion_score = self._calculate_occasion_suitability(outfit_items, occasion)
        
        total_score = (color_score * 0.3 + style_score * 0.25 + 
                      weather_score * 0.25 + occasion_score * 0.2)
        
        return min(100, total_score)
    
    def _calculate_color_harmony(self, outfit_items: List[Dict]) -> float:
        """計算顏色和諧度"""
        if len(outfit_items) < 2:
            return 50
        
        harmony_scores = []
        
        for i in range(len(outfit_items)):
            for j in range(i + 1, len(outfit_items)):
                color1 = outfit_items[i].get('primary_color', '').strip()
                color2 = outfit_items[j].get('primary_color', '').strip()
                
                score = self._get_color_compatibility_score(color1, color2)
                harmony_scores.append(score)
        
        return sum(harmony_scores) / len(harmony_scores) if harmony_scores else 50
    
    def _calculate_style_consistency(self, outfit_items: List[Dict], style_level: int) -> float:
        """計算風格一致性"""
        styles = [item.get('style', '').strip() for item in outfit_items if item.get('style')]
        
        if not styles:
            return 50
        
        preferred_styles = self.style_level_preferences.get(style_level, {}).get('styles', [])
        
        style_match_score = 0
        for style in styles:
            if style in preferred_styles:
                style_match_score += 100
            else:
                style_match_score += 40
        
        unique_styles = set(styles)
        consistency_bonus = 100 if len(unique_styles) == 1 else max(60, 100 - (len(unique_styles) - 1) * 15)
        
        return (style_match_score / len(styles) + consistency_bonus) / 2
    
    def _calculate_weather_appropriateness(self, outfit_items: List[Dict], weather: Dict) -> float:
        """計算天氣適應性"""
        temp = weather.get('temperature', 20)
        weather_main = weather.get('weather_main', 'Clear')
        
        appropriateness_score = 0
        total_items = len(outfit_items)
        
        for item in outfit_items:
            category = item.get('category', '').strip()
            material = item.get('material', '').lower()
            seasons = item.get('suitable_seasons', [])
            
            if isinstance(seasons, str):
                try:
                    seasons = json.loads(seasons)
                except:
                    seasons = [s.strip() for s in seasons.split(',')]
            
            item_score = 50
            
            # 溫度適應性
            if temp < 10:  # 寒冷
                if category in ['外套'] or any(keyword in material for keyword in ['毛', '厚', '保暖', '羊毛', '絨']):
                    item_score += 25
                if '冬季' in seasons:
                    item_score += 15
            elif temp < 18:  # 涼爽
                if category in ['外套', '上衣'] or any(keyword in material for keyword in ['薄', '長袖']):
                    item_score += 20
                if any(season in seasons for season in ['秋季', '春季']):
                    item_score += 15
            elif temp < 26:  # 舒適
                if any(season in seasons for season in ['春季', '秋季']):
                    item_score += 20
            else:  # 溫暖/炎熱
                if any(keyword in material for keyword in ['棉', '麻', '透氣', '薄', '涼爽']):
                    item_score += 25
                if '夏季' in seasons:
                    item_score += 15
            
            # 天氣狀況適應性
            if weather_main in ['Rain', 'Thunderstorm', 'Drizzle']:
                if category == '外套' or any(keyword in material for keyword in ['防水', '雨']):
                    item_score += 10
            
            appropriateness_score += min(100, item_score)
        
        return appropriateness_score / total_items
    
    def _calculate_occasion_suitability(self, outfit_items: List[Dict], occasion: str) -> float:
        """計算場合適用性"""
        suitability_score = 0
        total_items = len(outfit_items)
        
        occasion_mapping = {
            '正式': ['正式', '工作'],
            '日常': ['日常', '休閒'],
            '運動': ['運動'],
            '約會': ['約會', '日常'],
            '工作': ['工作', '正式']
        }
        
        suitable_occasions = occasion_mapping.get(occasion, [occasion])
        
        for item in outfit_items:
            item_occasions = item.get('suitable_occasions', [])
            if isinstance(item_occasions, str):
                try:
                    item_occasions = json.loads(item_occasions)
                except:
                    item_occasions = [s.strip() for s in item_occasions.split(',')]
            
            if any(occ in suitable_occasions for occ in item_occasions):
                suitability_score += 100
            elif not item_occasions:
                suitability_score += 70
            else:
                suitability_score += 40
        
        return suitability_score / total_items
    
    def generate_outfit_analysis(self, outfit_items: List[Dict], score: float, weather: Dict, occasion: str = "日常") -> str:
        """生成穿搭分析文字"""
        if not GEMINI_AVAILABLE or not self.model:
            return self._get_default_analysis_text(score)
        
        try:
            # 準備穿搭描述
            outfit_descriptions = []
            for item in outfit_items:
                desc = f"{item.get('name', '衣物')}"
                if item.get('primary_color'):
                    desc += f"({item['primary_color']})"
                outfit_descriptions.append(desc)
            
            outfit_text = " + ".join(outfit_descriptions)
            
            # 評分等級
            if score >= 80:
                grade = "優秀"
            elif score >= 70:
                grade = "良好" 
            elif score >= 60:
                grade = "及格"
            else:
                grade = "需改進"
            
            prompt = f"""
            請為這套穿搭組合提供專業的時尚分析：

            穿搭組合：{outfit_text}
            評分：{score:.1f}/100 ({grade})
            天氣：{weather.get('temperature', 20)}°C，{weather.get('weather_description', '晴朗')}
            場合：{occasion}

            請提供：
            1. 配色分析（顏色搭配的和諧度）
            2. 風格評價（整體風格的一致性）
            3. 實用性評估（適合天氣和場合）
            4. 推薦理由

            要求：
            - 使用繁體中文
            - 專業且友善的語調
            - 具體且有建設性的建議
            - 控制在100-120字
            - 以 "**AI穿搭分析** (評分:{score:.1f}/100-{grade})" 開頭
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"AI 穿搭分析生成錯誤: {e}")
            return self._get_default_analysis_text(score)
    
    def _get_default_analysis_text(self, score: float) -> str:
        """獲取預設分析文字"""
        if score >= 80:
            grade = "優秀"
            comment = "這套搭配在各方面都表現出色，色彩和諧且風格統一。"
        elif score >= 70:
            grade = "良好"
            comment = "整體搭配協調，具有良好的視覺效果和實用性。"
        elif score >= 60:
            grade = "及格"
            comment = "基本搭配合理，建議在色彩或風格上進行微調。"
        else:
            grade = "需改進"
            comment = "建議重新考慮色彩搭配或風格選擇，以提升整體效果。"
        
        return f"**AI穿搭分析** (評分:{score:.1f}/100-{grade}) - {comment} 根據當前天氣和場合需求，這套搭配能滿足基本的穿著需求。"

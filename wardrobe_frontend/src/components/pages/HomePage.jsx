import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { recommendationsAPI } from '@/lib/api';
import { Cloud, Sun, CloudRain, Thermometer, Wind, Droplets, RefreshCw, Sparkles } from 'lucide-react';

const HomePage = () => {
  const [weather, setWeather] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [location, setLocation] = useState('台北市');
  const [occasion, setOccasion] = useState('日常');
  const [styleLevel, setStyleLevel] = useState([3]);

  const styleDescriptions = {
    1: '保守經典',
    2: '簡約實用', 
    3: '日常時尚',
    4: '潮流前衛',
    5: '大膽創新'
  };

  const occasions = [
    { value: '日常', label: '日常' },
    { value: '正式', label: '正式' },
    { value: '運動', label: '運動' },
    { value: '約會', label: '約會' },
    { value: '工作', label: '工作' }
  ];

  useEffect(() => {
    fetchWeather();
  }, [location]);

  const fetchWeather = async () => {
    try {
      const response = await recommendationsAPI.getWeather(location);
      if (response.data.success) {
        setWeather(response.data.data);
      }
    } catch (error) {
      console.error('獲取天氣失敗:', error);
      // 使用模擬天氣資料
      setWeather({
        temperature: 27,
        humidity: 65,
        weather_description: '多雲',
        wind_speed: 1.03,
        city: location,
        temperature_category: '舒適'
      });
    }
  };

  const generateRecommendations = async () => {
    setLoading(true);
    try {
      const response = await recommendationsAPI.generate({
        user_id: 1,
        weather: weather,
        occasion: occasion,
        style_level: styleLevel[0]
      });
      
      if (response.data.success) {
        setRecommendations(response.data.data);
      }
    } catch (error) {
      console.error('生成推薦失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const getWeatherIcon = (description) => {
    if (description.includes('雨')) return <CloudRain className="w-6 h-6 text-blue-500" />;
    if (description.includes('雲')) return <Cloud className="w-6 h-6 text-gray-500" />;
    return <Sun className="w-6 h-6 text-yellow-500" />;
  };

  const getTemperatureColor = (temp) => {
    if (temp < 10) return 'text-blue-600';
    if (temp < 20) return 'text-green-600';
    if (temp < 30) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">今日智能穿搭推薦</h1>
        <p className="text-gray-600">根據天氣和個人風格，為您推薦最適合的穿搭</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 天氣資訊 */}
        <Card className="lg:col-span-1">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-lg font-medium">當前天氣</CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={fetchWeather}
              className="h-8 w-8 p-0"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </CardHeader>
          <CardContent>
            {weather ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {getWeatherIcon(weather.weather_description)}
                    <span className="text-sm text-gray-600">{weather.weather_description}</span>
                  </div>
                  <Badge variant="secondary">{weather.city}</Badge>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center space-x-2">
                    <Thermometer className="w-4 h-4 text-gray-500" />
                    <div>
                      <div className={`text-2xl font-bold ${getTemperatureColor(weather.temperature)}`}>
                        {weather.temperature}°C
                      </div>
                      <div className="text-xs text-gray-500">{weather.temperature_category}</div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Droplets className="w-4 h-4 text-blue-500" />
                      <span className="text-sm">{weather.humidity}%</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Wind className="w-4 h-4 text-gray-500" />
                      <span className="text-sm">{weather.wind_speed} m/s</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                <p className="text-sm text-gray-500">載入天氣資訊...</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* 設定面板 */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg font-medium">穿搭設定</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">地點</label>
                <Select value={location} onValueChange={setLocation}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="台北市">台北市</SelectItem>
                    <SelectItem value="新北市">新北市</SelectItem>
                    <SelectItem value="桃園市">桃園市</SelectItem>
                    <SelectItem value="台中市">台中市</SelectItem>
                    <SelectItem value="台南市">台南市</SelectItem>
                    <SelectItem value="高雄市">高雄市</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">場合</label>
                <Select value={occasion} onValueChange={setOccasion}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {occasions.map((occ) => (
                      <SelectItem key={occ.value} value={occ.value}>
                        {occ.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700">個人風格</label>
                <Badge variant="outline">{styleDescriptions[styleLevel[0]]}</Badge>
              </div>
              <Slider
                value={styleLevel}
                onValueChange={setStyleLevel}
                max={5}
                min={1}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>保守經典</span>
                <span>大膽創新</span>
              </div>
            </div>

            <Button 
              onClick={generateRecommendations} 
              disabled={loading || !weather}
              className="w-full"
              size="lg"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  生成中...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  生成AI穿搭推薦
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* 推薦結果 */}
      {recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium flex items-center">
              <Sparkles className="w-5 h-5 mr-2 text-blue-600" />
              AI穿搭推薦
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recommendations.map((outfit, index) => (
                <div key={outfit.id} className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-medium">推薦搭配 {index + 1}</h3>
                    <Badge variant={outfit.score >= 80 ? "default" : outfit.score >= 70 ? "secondary" : "outline"}>
                      {outfit.score.toFixed(1)}分
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2">
                    {outfit.items.map((item, itemIndex) => (
                      <div key={itemIndex} className="text-center">
                        <div className="w-full h-24 bg-gray-100 rounded-lg flex items-center justify-center mb-2">
                          {item.photo_path ? (
                            <img 
                              src={`http://localhost:5000${item.photo_path}`} 
                              alt={item.name}
                              className="w-full h-full object-cover rounded-lg"
                            />
                          ) : (
                            <Shirt className="w-8 h-8 text-gray-400" />
                          )}
                        </div>
                        <p className="text-xs text-gray-600">{item.name}</p>
                        <p className="text-xs text-gray-500">{item.category}</p>
                      </div>
                    ))}
                  </div>
                  
                  <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                    {outfit.explanation}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {recommendations.length === 0 && weather && (
        <Card>
          <CardContent className="text-center py-12">
            <Sparkles className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-600 mb-2">準備好了嗎？</h3>
            <p className="text-gray-500 mb-4">點擊上方按鈕，讓AI為您生成專屬的穿搭推薦</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default HomePage;


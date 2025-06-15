import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { recommendationsAPI } from '@/lib/api';
import { Sparkles, Heart, RefreshCw, Shirt } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const RecommendationsPage = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [weather, setWeather] = useState(null);
  const [occasion, setOccasion] = useState('日常');
  const [styleLevel, setStyleLevel] = useState([3]);
  const [location, setLocation] = useState('台北市');
  const { toast } = useToast();

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
        if (response.data.data.length === 0) {
          toast({
            title: "提示",
            description: response.data.message || "找不到適合的搭配組合，請嘗試調整設定或新增更多衣物",
          });
        }
      }
    } catch (error) {
      console.error('生成推薦失敗:', error);
      toast({
        title: "錯誤",
        description: "生成推薦失敗，請稍後再試",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const saveFavorite = async (outfit) => {
    try {
      const response = await recommendationsAPI.saveFavorite({
        user_id: 1,
        outfit_data: outfit,
        score: outfit.score
      });
      
      if (response.data.success) {
        toast({
          title: "成功",
          description: "穿搭已收藏",
        });
      }
    } catch (error) {
      console.error('收藏失敗:', error);
      toast({
        title: "錯誤",
        description: "收藏失敗，請稍後再試",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">穿搭推薦</h1>
        <p className="text-gray-600">根據您的喜好和當前天氣，為您推薦最佳穿搭</p>
      </div>

      {/* 設定面板 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-medium">推薦設定</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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

            <div className="space-y-2">
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
            </div>
          </div>

          <div className="flex justify-center">
            <Button 
              onClick={generateRecommendations} 
              disabled={loading}
              size="lg"
              className="px-8"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  生成中...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  生成穿搭推薦
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 推薦結果 */}
      {recommendations.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recommendations.map((outfit, index) => (
            <Card key={outfit.id} className="overflow-hidden">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">推薦搭配 {index + 1}</CardTitle>
                  <div className="flex items-center space-x-2">
                    <Badge variant={outfit.score >= 80 ? "default" : outfit.score >= 70 ? "secondary" : "outline"}>
                      {outfit.score.toFixed(1)}分
                    </Badge>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => saveFavorite(outfit)}
                      className="h-8 w-8 p-0"
                    >
                      <Heart className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* 衣物展示 */}
                <div className="grid grid-cols-2 gap-3">
                  {outfit.items.map((item, itemIndex) => (
                    <div key={itemIndex} className="text-center">
                      <div className="w-full h-32 bg-gray-100 rounded-lg flex items-center justify-center mb-2 overflow-hidden">
                        {item.photo_path ? (
                          <img 
                            src={`http://localhost:5000${item.photo_path}`} 
                            alt={item.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <Shirt className="w-8 h-8 text-gray-400" />
                        )}
                      </div>
                      <p className="text-sm font-medium text-gray-800">{item.name}</p>
                      <p className="text-xs text-gray-500">{item.category}</p>
                      {item.primary_color && (
                        <p className="text-xs text-gray-500">{item.primary_color}</p>
                      )}
                    </div>
                  ))}
                </div>
                
                {/* AI 分析說明 */}
                <div className="bg-blue-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-700 whitespace-pre-line">
                    {outfit.explanation}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* 空狀態 */}
      {recommendations.length === 0 && !loading && (
        <Card>
          <CardContent className="text-center py-12">
            <Sparkles className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-600 mb-2">準備好了嗎？</h3>
            <p className="text-gray-500 mb-4">設定您的偏好，讓AI為您生成專屬的穿搭推薦</p>
            <Button onClick={generateRecommendations} disabled={loading}>
              <Sparkles className="w-4 h-4 mr-2" />
              開始推薦
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default RecommendationsPage;


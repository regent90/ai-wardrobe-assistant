import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { recommendationsAPI } from '@/lib/api';
import { Heart, Trash2, Shirt, Calendar } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const FavoritesPage = () => {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchFavorites();
  }, []);

  const fetchFavorites = async () => {
    try {
      const response = await recommendationsAPI.getFavorites();
      if (response.data.success) {
        setFavorites(response.data.data);
      }
    } catch (error) {
      console.error('獲取收藏失敗:', error);
      toast({
        title: "錯誤",
        description: "無法載入收藏列表",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const deleteFavorite = async (id) => {
    if (!confirm('確定要刪除這個收藏嗎？')) return;
    
    try {
      const response = await recommendationsAPI.deleteFavorite(id);
      if (response.data.success) {
        toast({
          title: "成功",
          description: "收藏刪除成功",
        });
        fetchFavorites();
      }
    } catch (error) {
      console.error('刪除收藏失敗:', error);
      toast({
        title: "錯誤",
        description: "刪除收藏失敗",
        variant: "destructive",
      });
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">我的收藏</h1>
          <p className="text-gray-600">您收藏的穿搭組合</p>
        </div>
        <div className="flex items-center space-x-2">
          <Heart className="w-5 h-5 text-red-500" />
          <span className="text-lg font-medium text-gray-700">{favorites.length} 個收藏</span>
        </div>
      </div>

      {/* 收藏列表 */}
      {favorites.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <Heart className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-600 mb-2">還沒有收藏</h3>
            <p className="text-gray-500 mb-4">在推薦頁面找到喜歡的穿搭，點擊愛心收藏吧！</p>
            <Button onClick={() => window.location.href = '/recommendations'}>
              去看推薦
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {favorites.map((favorite) => {
            const outfitData = typeof favorite.outfit_data === 'string' 
              ? JSON.parse(favorite.outfit_data) 
              : favorite.outfit_data;
            
            return (
              <Card key={favorite.id} className="overflow-hidden">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">收藏穿搭</CardTitle>
                    <div className="flex items-center space-x-2">
                      {favorite.score && (
                        <Badge variant={favorite.score >= 80 ? "default" : favorite.score >= 70 ? "secondary" : "outline"}>
                          {favorite.score.toFixed(1)}分
                        </Badge>
                      )}
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => deleteFavorite(favorite.id)}
                        className="h-8 w-8 p-0"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  <div className="flex items-center text-sm text-gray-500">
                    <Calendar className="w-4 h-4 mr-1" />
                    {formatDate(favorite.created_at)}
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  {/* 衣物展示 */}
                  <div className="grid grid-cols-2 gap-3">
                    {outfitData.items && outfitData.items.map((item, itemIndex) => (
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
                  {outfitData.explanation && (
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <div className="text-sm text-gray-700 whitespace-pre-line">
                        {outfitData.explanation}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* 統計資訊 */}
      {favorites.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">收藏統計</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{favorites.length}</div>
                <div className="text-sm text-gray-500">總收藏數</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {favorites.filter(f => f.score >= 80).length}
                </div>
                <div className="text-sm text-gray-500">高分穿搭 (≥80分)</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {favorites.length > 0 ? (favorites.reduce((sum, f) => sum + (f.score || 0), 0) / favorites.length).toFixed(1) : 0}
                </div>
                <div className="text-sm text-gray-500">平均評分</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default FavoritesPage;


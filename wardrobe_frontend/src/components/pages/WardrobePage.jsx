import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { clothingAPI } from '@/lib/api';
import { Plus, Shirt, Edit, Trash2, Upload, Sparkles } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const WardrobePage = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [aiAnalyzing, setAiAnalyzing] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    style: '',
    material: '',
    suitable_seasons: [],
    suitable_occasions: []
  });
  const { toast } = useToast();

  const categories = ['上衣', '下著', '外套', '鞋子', '配件'];
  const styles = ['正式', '休閒', '運動', '浪漫', '復古', '現代'];
  const seasons = ['春季', '夏季', '秋季', '冬季'];
  const occasions = ['日常', '正式', '運動', '約會', '工作'];

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await clothingAPI.getAll();
      if (response.data.success) {
        setItems(response.data.data);
      }
    } catch (error) {
      console.error('獲取衣物失敗:', error);
      toast({
        title: "錯誤",
        description: "無法載入衣物資料",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
  };

  const analyzeWithAI = async () => {
    if (!selectedFile) {
      toast({
        title: "錯誤",
        description: "請先選擇圖片",
        variant: "destructive",
      });
      return;
    }

    setAiAnalyzing(true);
    try {
      const formDataForAI = new FormData();
      formDataForAI.append('photo', selectedFile);
      
      const response = await clothingAPI.analyze(formDataForAI);
      if (response.data.success) {
        const aiResult = response.data.data;
        setFormData({
          name: aiResult.name || '',
          category: aiResult.category || '',
          style: aiResult.style || '',
          material: aiResult.material || '',
          suitable_seasons: aiResult.suitable_seasons || [],
          suitable_occasions: aiResult.suitable_occasions || []
        });
        
        toast({
          title: "AI分析完成",
          description: "已自動填入分析結果，您可以進行調整",
        });
      }
    } catch (error) {
      console.error('AI分析失敗:', error);
      toast({
        title: "AI分析失敗",
        description: "請手動填入衣物資訊",
        variant: "destructive",
      });
    } finally {
      setAiAnalyzing(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const submitFormData = new FormData();
      submitFormData.append('user_id', '1');
      submitFormData.append('name', formData.name);
      submitFormData.append('category', formData.category);
      submitFormData.append('style', formData.style);
      submitFormData.append('material', formData.material);
      
      formData.suitable_seasons.forEach(season => {
        submitFormData.append('suitable_seasons', season);
      });
      
      formData.suitable_occasions.forEach(occasion => {
        submitFormData.append('suitable_occasions', occasion);
      });
      
      if (selectedFile) {
        submitFormData.append('photo', selectedFile);
      }

      const response = await clothingAPI.add(submitFormData);
      if (response.data.success) {
        toast({
          title: "成功",
          description: "衣物新增成功",
        });
        setIsAddDialogOpen(false);
        resetForm();
        fetchItems();
      }
    } catch (error) {
      console.error('新增衣物失敗:', error);
      toast({
        title: "錯誤",
        description: "新增衣物失敗",
        variant: "destructive",
      });
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('確定要刪除這件衣物嗎？')) return;
    
    try {
      const response = await clothingAPI.delete(id);
      if (response.data.success) {
        toast({
          title: "成功",
          description: "衣物刪除成功",
        });
        fetchItems();
      }
    } catch (error) {
      console.error('刪除衣物失敗:', error);
      toast({
        title: "錯誤",
        description: "刪除衣物失敗",
        variant: "destructive",
      });
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      category: '',
      style: '',
      material: '',
      suitable_seasons: [],
      suitable_occasions: []
    });
    setSelectedFile(null);
  };

  const handleSeasonChange = (season) => {
    setFormData(prev => ({
      ...prev,
      suitable_seasons: prev.suitable_seasons.includes(season)
        ? prev.suitable_seasons.filter(s => s !== season)
        : [...prev.suitable_seasons, season]
    }));
  };

  const handleOccasionChange = (occasion) => {
    setFormData(prev => ({
      ...prev,
      suitable_occasions: prev.suitable_occasions.includes(occasion)
        ? prev.suitable_occasions.filter(o => o !== occasion)
        : [...prev.suitable_occasions, occasion]
    }));
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
          <h1 className="text-3xl font-bold text-gray-800">我的衣櫃</h1>
          <p className="text-gray-600">管理您的衣物收藏</p>
        </div>
        
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button size="lg">
              <Plus className="w-4 h-4 mr-2" />
              新增衣物
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>新增衣物</DialogTitle>
            </DialogHeader>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* 圖片上傳 */}
              <div className="space-y-2">
                <Label>衣物圖片</Label>
                <div className="flex items-center space-x-2">
                  <Input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="flex-1"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={analyzeWithAI}
                    disabled={!selectedFile || aiAnalyzing}
                  >
                    {aiAnalyzing ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                        分析中...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4 mr-2" />
                        AI分析
                      </>
                    )}
                  </Button>
                </div>
                {selectedFile && (
                  <div className="mt-2">
                    <img
                      src={URL.createObjectURL(selectedFile)}
                      alt="預覽"
                      className="w-32 h-32 object-cover rounded-lg"
                    />
                  </div>
                )}
                <div className="text-sm text-blue-600 flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  <span>上傳圖片後，AI 將自動分析顏色和其他屬性</span>
                </div>
              </div>

              {/* 基本資訊 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">衣物名稱</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="category">類別</Label>
                  <Select value={formData.category} onValueChange={(value) => setFormData(prev => ({ ...prev, category: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="選擇類別" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map(category => (
                        <SelectItem key={category} value={category}>{category}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="style">風格</Label>
                  <Select value={formData.style} onValueChange={(value) => setFormData(prev => ({ ...prev, style: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="選擇風格" />
                    </SelectTrigger>
                    <SelectContent>
                      {styles.map(style => (
                        <SelectItem key={style} value={style}>{style}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="material">材質</Label>
                  <Input
                    id="material"
                    value={formData.material}
                    onChange={(e) => setFormData(prev => ({ ...prev, material: e.target.value }))}
                    placeholder="例如：棉質、聚酯纖維、羊毛等"
                  />
                </div>
              </div>

              {/* 適合季節 */}
              <div className="space-y-2">
                <Label>適合季節</Label>
                <div className="flex flex-wrap gap-2">
                  {seasons.map(season => (
                    <Button
                      key={season}
                      type="button"
                      variant={formData.suitable_seasons.includes(season) ? "default" : "outline"}
                      size="sm"
                      onClick={() => handleSeasonChange(season)}
                    >
                      {season}
                    </Button>
                  ))}
                </div>
              </div>

              {/* 適合場合 */}
              <div className="space-y-2">
                <Label>適合場合</Label>
                <div className="flex flex-wrap gap-2">
                  {occasions.map(occasion => (
                    <Button
                      key={occasion}
                      type="button"
                      variant={formData.suitable_occasions.includes(occasion) ? "default" : "outline"}
                      size="sm"
                      onClick={() => handleOccasionChange(occasion)}
                    >
                      {occasion}
                    </Button>
                  ))}
                </div>
              </div>

              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                  取消
                </Button>
                <Button type="submit">
                  新增衣物
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* 衣物網格 */}
      {items.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <Shirt className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-600 mb-2">衣櫃是空的</h3>
            <p className="text-gray-500 mb-4">開始新增您的第一件衣物吧！</p>
            <Button onClick={() => setIsAddDialogOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              新增衣物
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {items.map((item) => (
            <Card key={item.id} className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="aspect-square bg-gray-100 relative">
                {item.photo_path ? (
                  <img
                    src={`http://localhost:5000${item.photo_path}`}
                    alt={item.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Shirt className="w-12 h-12 text-gray-400" />
                  </div>
                )}
                
                <div className="absolute top-2 right-2 flex space-x-1">
                  <Button size="sm" variant="secondary" className="h-8 w-8 p-0">
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button 
                    size="sm" 
                    variant="destructive" 
                    className="h-8 w-8 p-0"
                    onClick={() => handleDelete(item.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              
              <CardContent className="p-4">
                <h3 className="font-medium text-gray-800 mb-1">{item.name}</h3>
                <div className="flex items-center justify-between mb-2">
                  <Badge variant="secondary">{item.category}</Badge>
                  {item.primary_color && (
                    <div className="flex items-center gap-1">
                      <span className="text-xs">🎨</span>
                      <span className="text-sm text-gray-500">{item.primary_color}</span>
                    </div>
                  )}
                </div>
                
                {item.style && (
                  <p className="text-sm text-gray-600 mb-2">{item.style}</p>
                )}
                
                {item.usage_count > 0 && (
                  <p className="text-xs text-gray-500">穿過 {item.usage_count} 次</p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default WardrobePage;

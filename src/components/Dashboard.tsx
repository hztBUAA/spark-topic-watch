import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Search, TrendingUp, MessageSquare, Hash, BarChart3, RefreshCw, Settings } from "lucide-react";
import { TrendChart } from "./TrendChart";
import { HotPostsList } from "./HotPostsList";
import { WordCloudComponent } from "./WordCloudComponent";
import { StatCard } from "./StatCard";
import { useDataContext } from "@/contexts/DataContext";
import { toast } from "sonner";

export const Dashboard = () => {
  const { 
    stats, 
    loading, 
    useMockData, 
    setUseMockData, 
    refreshData, 
    startMonitoring,
    searchKeywords
  } = useDataContext();
  
  const [searchKeyword, setSearchKeyword] = useState("");

  const handleSearch = async () => {
    if (!searchKeyword.trim()) {
      toast.error("请输入关键词");
      return;
    }
    
    const keywords = searchKeyword.split(',').map(k => k.trim()).filter(k => k);
    await startMonitoring(keywords);
    setSearchKeyword("");
  };

  const handleManualSearch = async () => {
    if (!searchKeyword.trim()) {
      toast.error("请输入关键词");
      return;
    }
    
    const keywords = searchKeyword.split(',').map(k => k.trim()).filter(k => k);
    await searchKeywords(keywords);
    setSearchKeyword("");
  };

  return (
    <div className="min-h-screen bg-background p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent mb-2">
              小红书舆情监测系统
            </h1>
            <p className="text-muted-foreground text-lg">
              实时监测热点趋势 · 挖掘爆款内容 · 洞察用户情绪
            </p>
          </div>
          <div className="flex items-center gap-4">
            {/* Mock/Real Data Toggle */}
            <div className="flex items-center gap-2 bg-card/50 backdrop-blur-sm border border-border/50 rounded-lg px-3 py-2">
              <Settings className="w-4 h-4 text-muted-foreground" />
              <Label htmlFor="mock-mode" className="text-sm">演示模式</Label>
              <Switch
                id="mock-mode"
                checked={useMockData}
                onCheckedChange={setUseMockData}
              />
            </div>
            
            <Button
              onClick={refreshData}
              disabled={loading}
              variant="outline"
              size="sm"
              className="bg-card/50 backdrop-blur-sm border-border/50"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              刷新
            </Button>
            
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input 
                placeholder="输入关键词，用逗号分隔..." 
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="pl-10 w-80 bg-card/50 backdrop-blur-sm border-border/50"
              />
            </div>
            
            <Button 
              onClick={handleSearch}
              disabled={loading}
              className="bg-gradient-primary hover:opacity-90 transition-opacity"
            >
              开始监测
            </Button>
            
            <Button 
              onClick={handleManualSearch}
              disabled={loading}
              variant="outline"
              className="bg-card/50 backdrop-blur-sm border-border/50"
            >
              立即搜索
            </Button>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="今日监测关键词"
            value={stats.total_keywords.toString()}
            change={`+${stats.keyword_growth}%`}
            icon={Hash}
            trend="up"
          />
          <StatCard
            title="热帖数量"
            value={stats.total_posts.toLocaleString()}
            change={`+${stats.posts_growth}%`}
            icon={TrendingUp}
            trend="up"
          />
          <StatCard
            title="总互动量"
            value={stats.total_interactions > 1000000 
              ? `${(stats.total_interactions / 1000000).toFixed(1)}M` 
              : stats.total_interactions.toLocaleString()}
            change={`+${stats.interactions_growth}%`}
            icon={MessageSquare}
            trend="up"
          />
          <StatCard
            title="情绪指数"
            value={`${stats.sentiment_score}%`}
            change={`+${stats.sentiment_growth}%`}
            icon={BarChart3}
            trend="up"
          />
        </div>
      </div>

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Chart - Takes 2 columns */}
        <div className="lg:col-span-2">
          <Card className="bg-card/50 backdrop-blur-sm border-border/50 shadow-glow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary" />
                关键词声量趋势
              </CardTitle>
            </CardHeader>
            <CardContent>
              <TrendChart />
            </CardContent>
          </Card>
        </div>

        {/* Word Cloud */}
        <div>
          <Card className="bg-card/50 backdrop-blur-sm border-border/50 shadow-accent-glow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Hash className="w-5 h-5 text-accent" />
                热词词云
              </CardTitle>
            </CardHeader>
            <CardContent className="h-80">
              <WordCloudComponent />
            </CardContent>
          </Card>
        </div>

        {/* Hot Posts List - Full width */}
        <div className="lg:col-span-3">
          <Card className="bg-card/50 backdrop-blur-sm border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-primary" />
                热帖排行榜
              </CardTitle>
            </CardHeader>
            <CardContent>
              <HotPostsList />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
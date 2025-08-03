import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, TrendingUp, MessageSquare, Hash, BarChart3 } from "lucide-react";
import { TrendChart } from "./TrendChart";
import { HotPostsList } from "./HotPostsList";
import { WordCloudComponent } from "./WordCloudComponent";
import { StatCard } from "./StatCard";

export const Dashboard = () => {
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
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input 
                placeholder="输入关键词开始监测..." 
                className="pl-10 w-80 bg-card/50 backdrop-blur-sm border-border/50"
              />
            </div>
            <Button className="bg-gradient-primary hover:opacity-90 transition-opacity">
              开始监测
            </Button>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="今日监测关键词"
            value="127"
            change="+12%"
            icon={Hash}
            trend="up"
          />
          <StatCard
            title="热帖数量"
            value="2,847"
            change="+23%"
            icon={TrendingUp}
            trend="up"
          />
          <StatCard
            title="总互动量"
            value="1.2M"
            change="+8%"
            icon={MessageSquare}
            trend="up"
          />
          <StatCard
            title="情绪指数"
            value="72%"
            change="+5%"
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
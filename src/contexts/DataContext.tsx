import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService, HotPost, KeywordTrend, WordCloudItem, SentimentData, StatsData } from '@/lib/api';
import { mockData } from '@/lib/mockData';
import { toast } from 'sonner';

interface DataContextType {
  // Data
  keywords: string[];
  trends: KeywordTrend[];
  hotPosts: HotPost[];
  wordCloud: WordCloudItem[];
  sentiment: SentimentData[];
  stats: StatsData;
  
  // UI State
  loading: boolean;
  error: string | null;
  useMockData: boolean;
  
  // Actions
  setUseMockData: (useMock: boolean) => void;
  refreshData: () => Promise<void>;
  startMonitoring: (keywords: string[]) => Promise<void>;
  searchKeywords: (keywords: string[]) => Promise<void>;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export const useDataContext = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useDataContext must be used within a DataProvider');
  }
  return context;
};

interface DataProviderProps {
  children: ReactNode;
}

export const DataProvider: React.FC<DataProviderProps> = ({ children }) => {
  const [keywords, setKeywords] = useState<string[]>([]);
  const [trends, setTrends] = useState<KeywordTrend[]>([]);
  const [hotPosts, setHotPosts] = useState<HotPost[]>([]);
  const [wordCloud, setWordCloud] = useState<WordCloudItem[]>([]);
  const [sentiment, setSentiment] = useState<SentimentData[]>([]);
  const [stats, setStats] = useState<StatsData>({
    total_keywords: 0,
    total_posts: 0,
    total_interactions: 0,
    sentiment_score: 0,
    keyword_growth: 0,
    posts_growth: 0,
    interactions_growth: 0,
    sentiment_growth: 0,
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [useMockData, setUseMockData] = useState(() => {
    const saved = localStorage.getItem('useMockData');
    return saved ? JSON.parse(saved) : true; // Default to mock mode
  });

  // Save mock mode preference
  useEffect(() => {
    localStorage.setItem('useMockData', JSON.stringify(useMockData));
  }, [useMockData]);

  const loadMockData = () => {
    setKeywords(mockData.keywords);
    setTrends(mockData.trends);
    setHotPosts(mockData.hotPosts);
    setWordCloud(mockData.wordCloud);
    setSentiment(mockData.sentiment);
    setStats(mockData.stats);
  };

  const loadRealData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [
        keywordsData,
        trendsData,
        hotPostsData,
        wordCloudData,
        sentimentData,
        statsData
      ] = await Promise.all([
        apiService.getKeywords().catch(() => []),
        apiService.getTrends().catch(() => []),
        apiService.getHotPosts().catch(() => []),
        apiService.getWordCloud().catch(() => []),
        apiService.getSentiment().catch(() => []),
        apiService.getStats().catch(() => mockData.stats)
      ]);

      setKeywords(keywordsData);
      setTrends(trendsData);
      setHotPosts(hotPostsData);
      setWordCloud(wordCloudData);
      setSentiment(sentimentData);
      setStats(statsData);
      
    } catch (err) {
      console.error('Failed to load real data:', err);
      setError('无法连接到后端服务，已切换到演示模式');
      toast.error('无法连接到后端服务，已切换到演示模式');
      setUseMockData(true);
      loadMockData();
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    if (useMockData) {
      loadMockData();
      toast.success('演示数据已刷新');
    } else {
      await loadRealData();
      toast.success('数据已刷新');
    }
  };

  const startMonitoring = async (searchKeywords: string[]) => {
    try {
      setLoading(true);
      
      if (useMockData) {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        toast.success(`已开始监测关键词: ${searchKeywords.join(', ')}`);
        return;
      }

      // Set keywords and start monitoring
      await apiService.setKeywords(searchKeywords);
      await apiService.startMonitoring();
      
      // Refresh data after starting monitoring
      await refreshData();
      
      toast.success(`已开始监测关键词: ${searchKeywords.join(', ')}`);
    } catch (err) {
      console.error('Failed to start monitoring:', err);
      toast.error('启动监测失败');
    } finally {
      setLoading(false);
    }
  };

  const searchKeywords = async (searchKeywords: string[]) => {
    try {
      setLoading(true);
      
      if (useMockData) {
        // Simulate search
        await new Promise(resolve => setTimeout(resolve, 1500));
        toast.success(`搜索完成: ${searchKeywords.join(', ')}`);
        return;
      }

      await apiService.startSearch(searchKeywords);
      toast.success(`搜索任务已启动: ${searchKeywords.join(', ')}`);
      
      // Refresh data after search
      setTimeout(() => {
        refreshData();
      }, 3000); // Refresh after 3 seconds to allow processing
      
    } catch (err) {
      console.error('Failed to search keywords:', err);
      toast.error('搜索失败');
    } finally {
      setLoading(false);
    }
  };

  // Load initial data
  useEffect(() => {
    if (useMockData) {
      loadMockData();
    } else {
      loadRealData();
    }
  }, [useMockData]);

  const value: DataContextType = {
    keywords,
    trends,
    hotPosts,
    wordCloud,
    sentiment,
    stats,
    loading,
    error,
    useMockData,
    setUseMockData,
    refreshData,
    startMonitoring,
    searchKeywords,
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
};
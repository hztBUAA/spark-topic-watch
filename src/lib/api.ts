import axios from 'axios';

// API Base URL - can be configured via environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// API Types
export interface HotPost {
  id: number;
  title: string;
  author: string;
  content: string;
  url: string;
  likes_count: number;
  comments_count: number;
  hot_score: number;
  keyword: string;
  publish_time: string;
}

export interface KeywordTrend {
  keyword: string;
  date: string;
  count: number;
}

export interface WordCloudItem {
  keyword: string;
  weight: number;
}

export interface SentimentData {
  keyword: string;
  positive_score: number;
  negative_score: number;
  neutral_score: number;
  date: string;
}

export interface StatsData {
  total_keywords: number;
  total_posts: number;
  total_interactions: number;
  sentiment_score: number;
  keyword_growth: number;
  posts_growth: number;
  interactions_growth: number;
  sentiment_growth: number;
}

// API Functions
export const apiService = {
  // Configuration
  async getKeywords(): Promise<string[]> {
    const response = await api.get('/config/keywords');
    return response.data.data.keywords || [];
  },

  async setKeywords(keywords: string[]): Promise<void> {
    await api.post('/config/keywords', { keywords });
  },

  // Data queries
  async getTrends(keyword?: string): Promise<KeywordTrend[]> {
    const url = keyword ? `/data/trends/${keyword}` : '/data/trends';
    const response = await api.get(url);
    return response.data.data || [];
  },

  async getHotPosts(keyword?: string, limit = 20): Promise<HotPost[]> {
    const response = await api.get('/data/hot-posts', {
      params: { keyword, limit }
    });
    return response.data.data || [];
  },

  async getWordCloud(keyword?: string): Promise<WordCloudItem[]> {
    const response = await api.get('/data/word-cloud', {
      params: { keyword }
    });
    return response.data.data || [];
  },

  async getSentiment(keyword?: string): Promise<SentimentData[]> {
    const url = keyword ? `/data/sentiment/${keyword}` : '/data/sentiment';
    const response = await api.get(url);
    return response.data.data || [];
  },

  async getStats(): Promise<StatsData> {
    const response = await api.get('/data/stats');
    return response.data.data;
  },

  // Scraping
  async startSearch(keywords: string[], limit = 20): Promise<void> {
    await api.post('/scraper/search', { keywords, limit });
  },

  async analyzeNote(url: string): Promise<any> {
    const response = await api.post('/scraper/analyze', { url });
    return response.data.data;
  },

  async getScrapingLogs(limit = 20): Promise<any[]> {
    const response = await api.get('/scraper/logs', { params: { limit } });
    return response.data.data || [];
  },

  // Monitor
  async startMonitoring(): Promise<void> {
    await api.post('/monitor/start');
  },

  async stopMonitoring(): Promise<void> {
    await api.post('/monitor/stop');
  },

  async getMonitorStatus(): Promise<any> {
    const response = await api.get('/monitor/status');
    return response.data.data;
  }
};
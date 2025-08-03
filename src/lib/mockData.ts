import { HotPost, KeywordTrend, WordCloudItem, SentimentData, StatsData } from './api';

// Mock data for development and testing
export const mockData = {
  keywords: ['美妆', '护肤', '化妆品', '口红', '面膜'],

  trends: [
    { keyword: '美妆', date: '2024-01-01', count: 1250 },
    { keyword: '美妆', date: '2024-01-02', count: 1380 },
    { keyword: '美妆', date: '2024-01-03', count: 1420 },
    { keyword: '美妆', date: '2024-01-04', count: 1380 },
    { keyword: '美妆', date: '2024-01-05', count: 1520 },
    { keyword: '美妆', date: '2024-01-06', count: 1680 },
    { keyword: '美妆', date: '2024-01-07', count: 1750 },
    { keyword: '护肤', date: '2024-01-01', count: 980 },
    { keyword: '护肤', date: '2024-01-02', count: 1050 },
    { keyword: '护肤', date: '2024-01-03', count: 1150 },
    { keyword: '护肤', date: '2024-01-04', count: 1220 },
    { keyword: '护肤', date: '2024-01-05', count: 1280 },
    { keyword: '护肤', date: '2024-01-06', count: 1350 },
    { keyword: '护肤', date: '2024-01-07', count: 1420 },
  ] as KeywordTrend[],

  hotPosts: [
    {
      id: 1,
      title: '秋冬必备！这款面霜真的太好用了！',
      author: '美妆达人小丽',
      content: '今天给大家分享一款我最近在用的面霜，真的是秋冬必备神器！质地丰润但不厚重，保湿效果超级棒...',
      url: 'https://www.xiaohongshu.com/explore/123',
      likes_count: 2845,
      comments_count: 456,
      hot_score: 2128.5,
      keyword: '面霜',
      publish_time: '2024-01-07T10:30:00Z'
    },
    {
      id: 2,
      title: '平价口红测评！20块钱也能买到好看的色号',
      author: '口红收集家',
      content: '姐妹们！今天来分享几支超平价但是超好看的口红，性价比真的绝了！',
      url: 'https://www.xiaohongshu.com/explore/124',
      likes_count: 1920,
      comments_count: 287,
      hot_score: 1430.1,
      keyword: '口红',
      publish_time: '2024-01-07T08:15:00Z'
    },
    {
      id: 3,
      title: '护肤小白必看！建立正确护肤流程',
      author: '护肤专家Annie',
      content: '很多小伙伴都在问护肤的正确顺序，今天详细讲解一下护肤的基本流程...',
      url: 'https://www.xiaohongshu.com/explore/125',
      likes_count: 1654,
      comments_count: 198,
      hot_score: 1217.8,
      keyword: '护肤',
      publish_time: '2024-01-07T06:45:00Z'
    },
    {
      id: 4,
      title: '眼妆教程｜日系清淡妆容画法',
      author: '化妆师小美',
      content: '今天教大家画一个超级温柔的日系眼妆，特别适合日常...',
      url: 'https://www.xiaohongshu.com/explore/126',
      likes_count: 1432,
      comments_count: 156,
      hot_score: 1049.2,
      keyword: '眼妆',
      publish_time: '2024-01-06T20:20:00Z'
    },
    {
      id: 5,
      title: '学生党必备！10块钱搞定全套底妆',
      author: '学生党省钱攻略',
      content: '穷学生的福音来了！用最少的钱打造完美底妆...',
      url: 'https://www.xiaohongshu.com/explore/127',
      likes_count: 1298,
      comments_count: 134,
      hot_score: 948.7,
      keyword: '底妆',
      publish_time: '2024-01-06T18:10:00Z'
    },
  ] as HotPost[],

  wordCloud: [
    { keyword: '面霜', weight: 95 },
    { keyword: '口红', weight: 88 },
    { keyword: '护肤', weight: 85 },
    { keyword: '眼妆', weight: 78 },
    { keyword: '底妆', weight: 72 },
    { keyword: '保湿', weight: 68 },
    { keyword: '美白', weight: 65 },
    { keyword: '防晒', weight: 62 },
    { keyword: '精华', weight: 58 },
    { keyword: '洁面', weight: 55 },
    { keyword: '爽肤水', weight: 52 },
    { keyword: '面膜', weight: 50 },
    { keyword: '眼霜', weight: 48 },
    { keyword: '粉底', weight: 45 },
    { keyword: '腮红', weight: 42 },
    { keyword: '眼影', weight: 40 },
    { keyword: '眉毛', weight: 38 },
    { keyword: '唇膏', weight: 35 },
    { keyword: '修容', weight: 32 },
    { keyword: '高光', weight: 30 },
  ] as WordCloudItem[],

  sentiment: [
    { keyword: '美妆', positive_score: 0.75, negative_score: 0.15, neutral_score: 0.10, date: '2024-01-07' },
    { keyword: '护肤', positive_score: 0.68, negative_score: 0.18, neutral_score: 0.14, date: '2024-01-07' },
    { keyword: '口红', positive_score: 0.82, negative_score: 0.10, neutral_score: 0.08, date: '2024-01-07' },
  ] as SentimentData[],

  stats: {
    total_keywords: 127,
    total_posts: 2847,
    total_interactions: 1200000,
    sentiment_score: 72,
    keyword_growth: 12,
    posts_growth: 23,
    interactions_growth: 8,
    sentiment_growth: 5,
  } as StatsData
};
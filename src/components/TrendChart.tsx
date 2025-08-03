import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useDataContext } from '@/contexts/DataContext';
import { useMemo } from 'react';

export const TrendChart = () => {
  const { trends } = useDataContext();
  
  // Transform trends data for chart
  const chartData = useMemo(() => {
    if (!trends.length) return [];
    
    // Group by date
    const grouped = trends.reduce((acc, trend) => {
      const date = new Date(trend.date).toLocaleDateString('zh-CN', { 
        month: 'short', 
        day: 'numeric' 
      });
      
      if (!acc[date]) {
        acc[date] = { name: date };
      }
      
      acc[date][trend.keyword] = trend.count;
      return acc;
    }, {} as Record<string, any>);
    
    return Object.values(grouped);
  }, [trends]);
  
  // Get unique keywords for lines
  const keywords = useMemo(() => {
    return Array.from(new Set(trends.map(t => t.keyword)));
  }, [trends]);
  
  const colors = ['hsl(var(--primary))', 'hsl(var(--accent))', 'hsl(var(--secondary))', '#8884d8', '#82ca9d'];
  
  if (!chartData.length) {
    return (
      <div className="h-80 flex items-center justify-center text-muted-foreground">
        暂无趋势数据
      </div>
    );
  }
  return (
    <div className="h-80 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
          <YAxis stroke="hsl(var(--muted-foreground))" />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'hsl(var(--popover))',
              border: '1px solid hsl(var(--border))',
              borderRadius: '8px',
            }}
          />
          <Legend />
          {keywords.map((keyword, index) => (
            <Line 
              key={keyword}
              type="monotone" 
              dataKey={keyword} 
              stroke={colors[index % colors.length]} 
              strokeWidth={3} 
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
import { useEffect, useRef, useMemo } from 'react';
import { useDataContext } from '@/contexts/DataContext';

export const WordCloudComponent = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const { wordCloud } = useDataContext();
  
  const words = useMemo(() => {
    if (!wordCloud.length) return [];
    
    const colors = [
      'hsl(var(--primary))',
      'hsl(var(--accent))',
      'hsl(var(--chart-3))',
      'hsl(var(--chart-4))',
      'hsl(var(--chart-5))',
    ];
    
    return wordCloud.map((item, index) => ({
      text: item.keyword,
      size: Math.max(12, Math.min(40, item.weight * 0.4 + 12)),
      color: colors[index % colors.length]
    }));
  }, [wordCloud]);
  
  if (!words.length) {
    return (
      <div className="h-full flex items-center justify-center text-muted-foreground">
        暂无词云数据
      </div>
    );
  }

  const getRandomPosition = () => ({
    x: Math.random() * 80 + 10,
    y: Math.random() * 80 + 10,
  });

  return (
    <div ref={containerRef} className="relative w-full h-full overflow-hidden">
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="relative w-full h-full">
          {words.map((word, index) => {
            const position = getRandomPosition();
            return (
              <div
                key={index}
                className="absolute transition-all duration-500 hover:scale-110 cursor-pointer"
                style={{
                  left: `${position.x}%`,
                  top: `${position.y}%`,
                  transform: 'translate(-50%, -50%)',
                  fontSize: `${word.size}px`,
                  color: word.color,
                  fontWeight: 'bold',
                  textShadow: '0 2px 4px rgba(0,0,0,0.3)',
                  animation: `float 6s ease-in-out infinite ${index * 0.5}s`,
                }}
              >
                {word.text}
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Gradient overlay for visual effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-accent/5 pointer-events-none" />
    </div>
  );
};
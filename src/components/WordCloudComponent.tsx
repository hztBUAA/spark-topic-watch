import { useEffect, useRef } from 'react';

const words = [
  { text: '医美', size: 40, color: 'hsl(var(--primary))' },
  { text: '护肤', size: 35, color: 'hsl(var(--accent))' },
  { text: '美白', size: 30, color: 'hsl(var(--chart-3))' },
  { text: '抗衰', size: 28, color: 'hsl(var(--chart-4))' },
  { text: '玻尿酸', size: 25, color: 'hsl(var(--primary))' },
  { text: '肉毒素', size: 23, color: 'hsl(var(--accent))' },
  { text: '热玛吉', size: 22, color: 'hsl(var(--chart-5))' },
  { text: '水光针', size: 20, color: 'hsl(var(--chart-3))' },
  { text: '线雕', size: 18, color: 'hsl(var(--primary))' },
  { text: '激光', size: 17, color: 'hsl(var(--accent))' },
  { text: '面膜', size: 16, color: 'hsl(var(--chart-4))' },
  { text: '精华', size: 15, color: 'hsl(var(--chart-5))' },
  { text: '洁面', size: 14, color: 'hsl(var(--chart-3))' },
  { text: '防晒', size: 13, color: 'hsl(var(--primary))' },
  { text: '眼霜', size: 12, color: 'hsl(var(--accent))' },
];

export const WordCloudComponent = () => {
  const containerRef = useRef<HTMLDivElement>(null);

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
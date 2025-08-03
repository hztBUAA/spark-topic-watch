import { Card, CardContent } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string;
  change: string;
  icon: LucideIcon;
  trend: "up" | "down";
}

export const StatCard = ({ title, value, change, icon: Icon, trend }: StatCardProps) => {
  return (
    <Card className="bg-card/50 backdrop-blur-sm border-border/50 hover:shadow-glow transition-all duration-300 animate-slide-in">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-muted-foreground text-sm font-medium">{title}</p>
            <p className="text-2xl font-bold mt-1">{value}</p>
            <p className={`text-sm mt-1 ${trend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
              {change} 相比昨日
            </p>
          </div>
          <div className="p-3 rounded-full bg-primary/10">
            <Icon className="w-6 h-6 text-primary" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
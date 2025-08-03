import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Heart, MessageCircle, Clock, ExternalLink } from "lucide-react";
import { useDataContext } from "@/contexts/DataContext";

export const HotPostsList = () => {
  const { hotPosts } = useDataContext();
  
  if (!hotPosts.length) {
    return (
      <div className="text-center text-muted-foreground py-8">
        暂无热帖数据
      </div>
    );
  }
  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[50px]">排名</TableHead>
            <TableHead>标题</TableHead>
            <TableHead className="w-[100px]">分类</TableHead>
            <TableHead className="w-[100px]">点赞数</TableHead>
            <TableHead className="w-[100px]">评论数</TableHead>
            <TableHead className="w-[100px]">热度分</TableHead>
            <TableHead className="w-[100px]">发布时间</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {hotPosts.slice(0, 10).map((post, index) => (
            <TableRow key={post.id} className="hover:bg-muted/50 transition-colors">
              <TableCell>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                  index === 0 ? 'bg-gradient-primary text-primary-foreground' :
                  index === 1 ? 'bg-accent text-accent-foreground' :
                  index === 2 ? 'bg-chart-3 text-foreground' :
                  'bg-muted text-muted-foreground'
                }`}>
                  {index + 1}
                </div>
              </TableCell>
              <TableCell>
                <div className="max-w-md">
                  <p className="font-medium line-clamp-2 hover:text-primary cursor-pointer transition-colors">
                    {post.title}
                  </p>
                </div>
              </TableCell>
              <TableCell>
                <Badge variant="secondary" className="bg-primary/10 text-primary">
                  {post.keyword}
                </Badge>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1 text-pink-400">
                  <Heart className="w-4 h-4" />
                  <span className="font-medium">{post.likes_count.toLocaleString()}</span>
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1 text-blue-400">
                  <MessageCircle className="w-4 h-4" />
                  <span className="font-medium">{post.comments_count.toLocaleString()}</span>
                </div>
              </TableCell>
              <TableCell>
                <span className="font-bold text-primary">{Math.round(post.hot_score).toLocaleString()}</span>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 text-muted-foreground">
                    <Clock className="w-4 h-4" />
                    <span className="text-sm">
                      {new Date(post.publish_time).toLocaleDateString('zh-CN')}
                    </span>
                  </div>
                  <a 
                    href={post.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-muted-foreground hover:text-primary transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};
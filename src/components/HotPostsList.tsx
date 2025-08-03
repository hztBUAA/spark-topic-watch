import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Heart, MessageCircle, Clock } from "lucide-react";

const hotPosts = [
  {
    id: 1,
    title: "2024年最新医美项目推荐！这些项目真的太绝了",
    likes: 12800,
    comments: 892,
    time: "2小时前",
    score: 9564,
    tag: "医美"
  },
  {
    id: 2,
    title: "亲测有效的护肤步骤，皮肤状态肉眼可见的变好",
    likes: 8900,
    comments: 567,
    score: 6400,
    tag: "护肤"
  },
  {
    id: 3,
    title: "医美避雷指南！这些坑千万不要踩",
    likes: 7200,
    comments: 1205,
    score: 5400,
    tag: "医美"
  },
  {
    id: 4,
    title: "学生党也能做的平价医美项目分享",
    likes: 6500,
    comments: 423,
    score: 4678,
    tag: "医美"
  },
  {
    id: 5,
    title: "医美后护理全攻略，照着做恢复更快",
    likes: 5800,
    comments: 298,
    score: 4149,
    tag: "医美"
  }
];

export const HotPostsList = () => {
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
          {hotPosts.map((post, index) => (
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
                  {post.tag}
                </Badge>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1 text-pink-400">
                  <Heart className="w-4 h-4" />
                  <span className="font-medium">{post.likes.toLocaleString()}</span>
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1 text-blue-400">
                  <MessageCircle className="w-4 h-4" />
                  <span className="font-medium">{post.comments.toLocaleString()}</span>
                </div>
              </TableCell>
              <TableCell>
                <span className="font-bold text-primary">{post.score.toLocaleString()}</span>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1 text-muted-foreground">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm">{post.time}</span>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};
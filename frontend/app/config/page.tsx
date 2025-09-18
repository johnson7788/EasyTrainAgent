import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

export default function ConfigPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">基本配置</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Docker 配置</CardTitle>
          <CardDescription>配置 Docker 相关信息</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid w-full max-w-sm items-center gap-1.5">
            <Label htmlFor="docker-registry">Docker Registry</Label>
            <Input id="docker-registry" placeholder="e.g., docker.io" />
          </div>
          <div className="grid w-full max-w-sm items-center gap-1.5">
            <Label htmlFor="docker-username">用户名</Label>
            <Input id="docker-username" placeholder="Username" />
          </div>
          <div className="grid w-full max-w-sm items-center gap-1.5">
            <Label htmlFor="docker-password">密码</Label>
            <Input id="docker-password" type="password" placeholder="Password" />
          </div>
          <Button>保存 Docker 配置</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Weights & Biases (W&B) 配置</CardTitle>
          <CardDescription>配置 W&B 用于实验跟踪</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid w-full max-w-sm items-center gap-1.5">
            <Label htmlFor="wandb-apikey">API Key</Label>
            <Input id="wandb-apikey" type="password" placeholder="Your W&B API Key" />
          </div>
          <div className="grid w-full max-w-sm items-center gap-1.5">
            <Label htmlFor="wandb-entity">Entity</Label>
            <Input id="wandb-entity" placeholder="Your W&B entity (username or team)" />
          </div>
          <div className="grid w-full max-w-sm items-center gap-1.5">
            <Label htmlFor="wandb-project">Project</Label>
            <Input id="wandb-project" placeholder="Default project name" />
          </div>
          <Button>保存 W&B 配置</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>GPU 配置</CardTitle>
          <CardDescription>管理和查看 GPU 资源</CardDescription>
        </CardHeader>
        <CardContent>
          {/* Placeholder for GPU info display */}
          <p>GPU 信息将在此处显示。</p>
          <div className="mt-4">
            <Button variant="outline">刷新 GPU 状态</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

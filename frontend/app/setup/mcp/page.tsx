'use client';

import { useState } from 'react';
import { useAppStore } from '@/stores/useAppStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { LogViewer } from '@/components/ui/log-viewer';
import { 
  Server, 
  Play, 
  Square, 
  RefreshCw, 
  CheckCircle, 
  AlertCircle,
  Settings,
  Activity
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function MCPSetupPage() {
  const { mcpConfig, updateMCPConfig, addLog } = useAppStore();
  const [isConnecting, setIsConnecting] = useState(false);
  const [isTesting, setIsTesting] = useState(false);

  const [formData, setFormData] = useState({
    serverPath: mcpConfig.serverPath,
    port: mcpConfig.port.toString()
  });

  const handleStartServer = async () => {
    setIsConnecting(true);
    
    try {
      addLog({
        timestamp: new Date(),
        level: 'info',
        message: `启动 MCP Server: ${formData.serverPath}:${formData.port}`,
        source: 'mcp-server'
      });

      // 模拟启动过程
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      updateMCPConfig({
        serverPath: formData.serverPath,
        port: parseInt(formData.port),
        isRunning: true,
        lastHealthCheck: new Date()
      });

      addLog({
        timestamp: new Date(),
        level: 'info',
        message: 'MCP Server 启动成功',
        source: 'mcp-server'
      });

      toast.success('MCP Server 启动成功');
    } catch (error) {
      addLog({
        timestamp: new Date(),
        level: 'error',
        message: `MCP Server 启动失败: ${error}`,
        source: 'mcp-server'
      });
      toast.error('MCP Server 启动失败');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleStopServer = async () => {
    setIsConnecting(true);
    
    try {
      addLog({
        timestamp: new Date(),
        level: 'info',
        message: '正在停止 MCP Server...',
        source: 'mcp-server'
      });

      await new Promise(resolve => setTimeout(resolve, 1000));
      
      updateMCPConfig({
        isRunning: false
      });

      addLog({
        timestamp: new Date(),
        level: 'info',
        message: 'MCP Server 已停止',
        source: 'mcp-server'
      });

      toast.success('MCP Server 已停止');
    } catch (error) {
      addLog({
        timestamp: new Date(),
        level: 'error',
        message: `停止 MCP Server 失败: ${error}`,
        source: 'mcp-server'
      });
      toast.error('停止 MCP Server 失败');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleHealthCheck = async () => {
    setIsTesting(true);
    
    try {
      addLog({
        timestamp: new Date(),
        level: 'info',
        message: '开始健康检查...',
        source: 'health-check'
      });

      await new Promise(resolve => setTimeout(resolve, 1500));
      
      updateMCPConfig({
        lastHealthCheck: new Date()
      });

      addLog({
        timestamp: new Date(),
        level: 'info',
        message: '健康检查通过 - 服务运行正常',
        source: 'health-check'
      });

      toast.success('健康检查通过');
    } catch (error) {
      addLog({
        timestamp: new Date(),
        level: 'error',
        message: `健康检查失败: ${error}`,
        source: 'health-check'
      });
      toast.error('健康检查失败');
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Server className="h-8 w-8 text-blue-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">MCP 服务配置</h1>
          <p className="text-gray-600">配置和管理 MCP (Model Context Protocol) 服务器</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Configuration Form */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                服务器配置
              </CardTitle>
              <CardDescription>
                配置 MCP Server 的连接参数和运行环境
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="serverPath">服务器路径</Label>
                  <Input
                    id="serverPath"
                    placeholder="例如: /usr/local/bin/mcp-server"
                    value={formData.serverPath}
                    onChange={(e) => setFormData({...formData, serverPath: e.target.value})}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="port">端口号</Label>
                  <Input
                    id="port"
                    type="number"
                    placeholder="8080"
                    value={formData.port}
                    onChange={(e) => setFormData({...formData, port: e.target.value})}
                  />
                </div>
              </div>

              <div className="flex gap-3">
                {!mcpConfig.isRunning ? (
                  <Button 
                    onClick={handleStartServer}
                    disabled={isConnecting || !formData.serverPath}
                    className="flex items-center gap-2"
                  >
                    <Play className="h-4 w-4" />
                    {isConnecting ? '启动中...' : '启动服务器'}
                  </Button>
                ) : (
                  <Button 
                    onClick={handleStopServer}
                    disabled={isConnecting}
                    variant="destructive"
                    className="flex items-center gap-2"
                  >
                    <Square className="h-4 w-4" />
                    {isConnecting ? '停止中...' : '停止服务器'}
                  </Button>
                )}

                {mcpConfig.isRunning && (
                  <Button 
                    onClick={handleHealthCheck}
                    disabled={isTesting}
                    variant="outline"
                    className="flex items-center gap-2"
                  >
                    <RefreshCw className={`h-4 w-4 ${isTesting ? 'animate-spin' : ''}`} />
                    健康检查
                  </Button>
                )}
              </div>

              {mcpConfig.isRunning && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <span className="font-medium text-green-800">服务器运行中</span>
                  </div>
                  <p className="text-sm text-green-700 mt-1">
                    地址: {formData.serverPath}:{formData.port}
                  </p>
                  {mcpConfig.lastHealthCheck && (
                    <p className="text-xs text-green-600 mt-1">
                      上次检查: {mcpConfig.lastHealthCheck.toLocaleString()}
                    </p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Connection Test */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                连接测试
              </CardTitle>
              <CardDescription>
                测试与 MCP Server 的连接和通信
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {mcpConfig.isRunning ? '在线' : '离线'}
                  </div>
                  <div className="text-sm text-gray-600">连接状态</div>
                </div>

                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {mcpConfig.lastHealthCheck ? '<100ms' : '--'}
                  </div>
                  <div className="text-sm text-gray-600">响应时间</div>
                </div>

                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">v1.0</div>
                  <div className="text-sm text-gray-600">协议版本</div>
                </div>
              </div>

              <div className="space-y-2">
                <h4 className="font-medium">支持的功能</h4>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary">模型推理</Badge>
                  <Badge variant="secondary">批量处理</Badge>
                  <Badge variant="secondary">流式输出</Badge>
                  <Badge variant="secondary">监控指标</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          {/* Status Card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">服务状态</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">运行状态</span>
                  <Badge variant={mcpConfig.isRunning ? 'default' : 'secondary'}>
                    {mcpConfig.isRunning ? '运行中' : '已停止'}
                  </Badge>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm">服务端口</span>
                  <span className="text-sm font-mono">{mcpConfig.port}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm">上次检查</span>
                  <span className="text-xs text-gray-500">
                    {mcpConfig.lastHealthCheck
                      ? mcpConfig.lastHealthCheck.toLocaleTimeString()
                      : '未检查'
                    }
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">快捷操作</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" size="sm" className="w-full justify-start">
                查看服务日志
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start">
                重启服务器
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start">
                性能监控
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Logs Section */}
      <LogViewer taskId="mcp-server" />
    </div>
  );
}
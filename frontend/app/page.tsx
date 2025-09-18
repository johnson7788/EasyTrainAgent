'use client';

import { useAppStore } from '@/stores/useAppStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { MetricCard } from '@/components/ui/metric-card';
import { StepIndicator } from '@/components/ui/step-indicator';
import { 
  Activity, 
  Clock, 
  CheckCircle, 
  AlertTriangle,
  TrendingUp,
  Database,
  Brain,
  Rocket
} from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function Dashboard() {
  const { trainingSteps, currentTasks, mcpConfig } = useAppStore();
  const [backendStatus, setBackendStatus] = useState<'detecting' | 'online' | 'offline'>('detecting');

  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const response = await fetch('/api/ping');
        if (response.ok) {
          setBackendStatus('online');
        } else {
          setBackendStatus('offline');
        }
      } catch (error) {
        setBackendStatus('offline');
      }
    };

    checkBackendStatus();
  }, []);

  const completedSteps = trainingSteps.filter(step => step.status === 'completed').length;
  const runningTasks = currentTasks.filter(task => task.status === 'running').length;
  const errorTasks = currentTasks.filter(task => task.status === 'error').length;

  const metrics = [
    {
      name: '完成步骤',
      value: completedSteps,
      change: 5.2,
      trend: 'up' as const
    },
    {
      name: '运行任务',
      value: runningTasks,
      change: -2.1,
      trend: 'down' as const
    },
    {
      name: '错误任务',
      value: errorTasks,
      change: 0,
      trend: 'stable' as const
    },
    {
      name: '总进度',
      value: (trainingSteps.length > 0 ? (completedSteps / trainingSteps.length) * 100 : 0),
      change: 12.5,
      trend: 'up' as const
    }
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold text-gray-900">训练流程仪表板</h1>
        <p className="text-gray-600">监控和管理您的AI模型训练流程</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">后端服务状态</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                backendStatus === 'online'
                  ? 'bg-green-500'
                  : backendStatus === 'offline'
                  ? 'bg-red-500'
                  : 'bg-yellow-500'
              }`} />
              <span className="text-sm">
                {backendStatus === 'online'
                  ? '运行中'
                  : backendStatus === 'offline'
                  ? '已停止'
                  : '检测中...'}
              </span>
            </div>
          </CardContent>
        </Card>
        {metrics.map((metric, index) => (
          <MetricCard 
            key={metric.name} 
            metric={metric}
            format={index === 3 ? 'percentage' : 'number'}
          />
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Training Progress */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                训练流程进度
              </CardTitle>
              <CardDescription>
                当前训练步骤和整体进度概览
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <StepIndicator 
                  steps={trainingSteps.slice(0, 5)} 
                  currentStep={0}
                  orientation="vertical"
                />
                <div className="flex justify-between items-center pt-4 border-t">
                  <span className="text-sm text-gray-600">
                    {completedSteps} / {trainingSteps.length} 步骤完成
                  </span>
                  <Link href="/wizard">
                    <Button size="sm">
                      继续训练
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* System Status */}
        <div className="space-y-6">
          {/* MCP Status */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">MCP 服务状态</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${
                    mcpConfig.isRunning ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <span className="text-sm">
                    {mcpConfig.isRunning ? '运行中' : '已停止'}
                  </span>
                </div>
                <Link href="/setup/mcp">
                  <Button variant="outline" size="sm">
                    配置
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">快捷操作</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Link href="/data" className="block">
                <Button variant="outline" className="w-full justify-start">
                  <Database className="h-4 w-4 mr-2" />
                  数据管理
                </Button>
              </Link>
              <Link href="/train" className="block">
                <Button variant="outline" className="w-full justify-start">
                  <Brain className="h-4 w-4 mr-2" />
                  开始训练
                </Button>
              </Link>
              <Link href="/deploy" className="block">
                <Button variant="outline" className="w-full justify-start">
                  <Rocket className="h-4 w-4 mr-2" />
                  模型部署
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">最近活动</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>MCP 服务器配置完成</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-blue-500" />
                  <span>开始生成训练数据</span>
                </div>
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-yellow-500" />
                  <span>等待数据标注完成</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

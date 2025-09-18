'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './card';
import { Badge } from './badge';
import { Button } from './button';
import { Progress } from './progress';
import { LogViewer } from './log-viewer';
import { AlertCircle, CheckCircle, Clock, Play, Pause, RotateCcw } from 'lucide-react';
import { Task } from '@/types';
import { cn } from '@/lib/utils';

interface TaskCardProps {
  task: Task;
  onExecute?: () => void;
  onPause?: () => void;
  onResume?: () => void;
  onReset?: () => void;
  showLogs?: boolean;
  children?: React.ReactNode;
}

const statusConfig = {
  pending: { color: 'bg-gray-500', icon: Clock, label: '等待中' },
  running: { color: 'bg-blue-500', icon: Play, label: '运行中' },
  success: { color: 'bg-green-500', icon: CheckCircle, label: '成功' },
  error: { color: 'bg-red-500', icon: AlertCircle, label: '失败' }
};

export function TaskCard({
  task,
  onExecute,
  onPause,
  onResume,
  onReset,
  showLogs = false,
  children
}: TaskCardProps) {
  const [logsExpanded, setLogsExpanded] = useState(false);
  const config = statusConfig[task.status];
  const StatusIcon = config.icon;

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={cn('w-3 h-3 rounded-full', config.color)} />
            <div>
              <CardTitle className="text-lg">{task.title}</CardTitle>
              <CardDescription>{task.description}</CardDescription>
            </div>
          </div>
          <Badge variant="outline" className="flex items-center gap-1">
            <StatusIcon className="h-3 w-3" />
            {config.label}
          </Badge>
        </div>

        {task.progress !== undefined && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>进度</span>
              <span>{task.progress}%</span>
            </div>
            <Progress value={task.progress} className="h-2" />
          </div>
        )}
      </CardHeader>

      <CardContent className="space-y-4">
        {children && (
          <div className="space-y-4">
            {children}
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {task.status === 'pending' && onExecute && (
            <Button onClick={onExecute} size="sm">
              <Play className="h-4 w-4 mr-2" />
              开始执行
            </Button>
          )}

          {task.status === 'running' && (
            <>
              {onPause && (
                <Button onClick={onPause} variant="outline" size="sm">
                  <Pause className="h-4 w-4 mr-2" />
                  暂停
                </Button>
              )}
            </>
          )}

          {(task.status === 'error' || task.status === 'success') && onReset && (
            <Button onClick={onReset} variant="outline" size="sm">
              <RotateCcw className="h-4 w-4 mr-2" />
              重置
            </Button>
          )}

          {showLogs && (
            <Button
              onClick={() => setLogsExpanded(!logsExpanded)}
              variant="ghost"
              size="sm"
            >
              {logsExpanded ? '收起日志' : '查看日志'}
            </Button>
          )}
        </div>

        {showLogs && logsExpanded && (
          <LogViewer taskId={task.id} />
        )}
      </CardContent>
    </Card>
  );
}
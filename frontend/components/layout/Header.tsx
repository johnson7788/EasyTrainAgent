'use client';

import { Bell, Settings, User, Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAppStore } from '@/stores/useAppStore';

export function Header() {
  const { currentTasks, toggleSidebar } = useAppStore();
  const runningTasks = currentTasks.filter(task => task.status === 'running');

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={toggleSidebar}>
            <Menu className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">EASYTrainAgent</h1>
            <p className="text-sm text-gray-600">AI训练流程管理平台</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {runningTasks.length > 0 && (
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600">
                {runningTasks.length} 个任务正在运行
              </span>
            </div>
          )}

          <Button variant="ghost" size="sm" className="relative">
            <Bell className="h-5 w-5" />
            {runningTasks.length > 0 && (
              <Badge className="absolute -top-1 -right-1 px-1 min-w-[1.25rem] h-5">
                {runningTasks.length}
              </Badge>
            )}
          </Button>

          <Button variant="ghost" size="sm">
            <Settings className="h-5 w-5" />
          </Button>

          <Button variant="ghost" size="sm">
            <User className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}
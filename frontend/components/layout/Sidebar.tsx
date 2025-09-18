'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/stores/useAppStore';
import {
  Home,
  Zap,
  Database,
  Brain,
  BarChart3,
  Rocket,
  Tag,
  FileText,
  Settings,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { Button } from '@/components/ui/button';

const navigation = [
  { name: '仪表板', href: '/', icon: Home },
  { name: '训练向导', href: '/wizard', icon: Zap },
  { name: 'MCP 配置', href: '/setup/mcp', icon: Settings },
  { name: '数据管理', href: '/data', icon: Database },
  { name: '数据标注', href: '/labeling', icon: Tag },
  { name: '模型训练', href: '/train', icon: Brain },
  { name: '模型评估', href: '/eval', icon: BarChart3 },
  { name: '模型部署', href: '/deploy', icon: Rocket },
  { name: '日志查看', href: '/logs', icon: FileText }
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarCollapsed, toggleSidebar, trainingSteps, currentStep } = useAppStore();

  return (
    <div
      className={cn(
        'bg-gray-900 text-white transition-all duration-300 flex flex-col',
        sidebarCollapsed ? 'w-16' : 'w-64'
      )}
    >
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        {!sidebarCollapsed && (
          <span className="font-semibold text-lg">导航菜单</span>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleSidebar}
          className="text-gray-400 hover:text-white"
        >
          {sidebarCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href || 
            (item.href !== '/' && pathname.startsWith(item.href));
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white',
                sidebarCollapsed && 'justify-center'
              )}
            >
              <item.icon className={cn('h-5 w-5', sidebarCollapsed && 'mx-auto')} />
              {!sidebarCollapsed && <span>{item.name}</span>}
            </Link>
          );
        })}
      </nav>

      {!sidebarCollapsed && pathname === '/wizard' && (
        <div className="p-4 border-t border-gray-700">
          <h3 className="text-sm font-semibold text-gray-400 mb-3">训练步骤</h3>
          <div className="space-y-2">
            {trainingSteps.map((step, index) => (
              <div
                key={step.id}
                className={cn(
                  'flex items-center gap-2 text-xs',
                  index === currentStep ? 'text-blue-400' : 'text-gray-500'
                )}
              >
                <div className={cn(
                  'w-2 h-2 rounded-full flex-shrink-0',
                  step.status === 'completed' ? 'bg-green-500' :
                  step.status === 'running' ? 'bg-blue-500 animate-pulse' :
                  step.status === 'error' ? 'bg-red-500' :
                  'bg-gray-600'
                )} />
                <span className="truncate">{step.title}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
'use client';

import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './card';
import { Badge } from './badge';
import { Button } from './button';
import { Input } from './input';
import { ScrollArea } from './scroll-area';
import { Search, Download, Trash2, Filter } from 'lucide-react';
import { useAppStore } from '@/stores/useAppStore';
import { LogEntry } from '@/types';

interface LogViewerProps {
  taskId?: string;
  maxHeight?: string;
}

const logLevelColors = {
  info: 'bg-blue-100 text-blue-800',
  warning: 'bg-yellow-100 text-yellow-800',
  error: 'bg-red-100 text-red-800',
  debug: 'bg-gray-100 text-gray-800'
};

export function LogViewer({ taskId, maxHeight = '300px' }: LogViewerProps) {
  const { logs, clearLogs } = useAppStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [levelFilter, setLevelFilter] = useState<string[]>(['info', 'warning', 'error', 'debug']);
  const [autoScroll, setAutoScroll] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);

  // 过滤日志
  const filteredLogs = logs.filter(log => {
    const matchesTask = !taskId || log.source === taskId;
    const matchesLevel = levelFilter.includes(log.level);
    const matchesSearch = !searchTerm || 
      log.message.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesTask && matchesLevel && matchesSearch;
  });

  // 自动滚动到底部
  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [filteredLogs, autoScroll]);

  const toggleLevelFilter = (level: string) => {
    setLevelFilter(prev => 
      prev.includes(level)
        ? prev.filter(l => l !== level)
        : [...prev, level]
    );
  };

  const exportLogs = () => {
    const content = filteredLogs
      .map(log => `[${log.timestamp.toISOString()}] [${log.level.toUpperCase()}] ${log.message}`)
      .join('\n');
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs-${new Date().toISOString()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">实时日志</CardTitle>
          <div className="flex items-center gap-2">
            <Button onClick={exportLogs} variant="outline" size="sm">
              <Download className="h-4 w-4" />
            </Button>
            <Button onClick={clearLogs} variant="outline" size="sm">
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 items-center">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="搜索日志..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <div className="flex gap-1">
            {Object.keys(logLevelColors).map(level => (
              <Badge
                key={level}
                variant={levelFilter.includes(level) ? 'default' : 'outline'}
                className="cursor-pointer"
                onClick={() => toggleLevelFilter(level)}
              >
                {level}
              </Badge>
            ))}
          </div>

          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded"
            />
            自动滚动
          </label>
        </div>
      </CardHeader>

      <CardContent>
        <ScrollArea 
          ref={scrollRef}
          style={{ height: maxHeight }}
          className="border rounded-lg p-3 font-mono text-sm bg-gray-50"
        >
          {filteredLogs.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              暂无日志记录
            </div>
          ) : (
            <div className="space-y-1">
              {filteredLogs.map((log) => (
                <div key={log.id} className="flex items-start gap-3">
                  <span className="text-gray-400 text-xs flex-shrink-0">
                    {log.timestamp.toLocaleTimeString()}
                  </span>
                  <Badge
                    variant="outline"
                    className={`text-xs flex-shrink-0 ${logLevelColors[log.level]}`}
                  >
                    {log.level.toUpperCase()}
                  </Badge>
                  <span className="flex-1 break-all">{log.message}</span>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
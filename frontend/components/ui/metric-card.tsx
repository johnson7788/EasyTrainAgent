'use client';

import { Card, CardContent, CardHeader, CardTitle } from './card';
import { Badge } from './badge';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { MetricData } from '@/types';

interface MetricCardProps {
  metric: MetricData;
  format?: 'number' | 'percentage' | 'duration';
  showTrend?: boolean;
}

export function MetricCard({ 
  metric, 
  format = 'number', 
  showTrend = true 
}: MetricCardProps) {
  const formatValue = (value: number) => {
    switch (format) {
      case 'percentage':
        return `${value.toFixed(1)}%`;
      case 'duration':
        return `${value.toFixed(1)}s`;
      default:
        return value.toLocaleString();
    }
  };

  const getTrendIcon = () => {
    if (!metric.trend) return Minus;
    return metric.trend === 'up' ? TrendingUp : TrendingDown;
  };

  const getTrendColor = () => {
    if (!metric.trend) return 'text-gray-400';
    return metric.trend === 'up' ? 'text-green-500' : 'text-red-500';
  };

  const TrendIcon = getTrendIcon();

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">
          {metric.name}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="text-2xl font-bold">
            {formatValue(metric.value)}
          </div>
          
          {showTrend && metric.change !== undefined && (
            <div className="flex items-center gap-1">
              <TrendIcon className={`h-4 w-4 ${getTrendColor()}`} />
              <Badge
                variant="outline"
                className={`text-xs ${getTrendColor()}`}
              >
                {metric.change > 0 ? '+' : ''}{metric.change.toFixed(1)}%
              </Badge>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
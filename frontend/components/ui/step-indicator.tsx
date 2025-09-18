'use client';

import { cn } from '@/lib/utils';
import { CheckCircle, AlertCircle, Clock, Loader } from 'lucide-react';
import { TrainingStep } from '@/types';

interface StepIndicatorProps {
  steps: TrainingStep[];
  currentStep: number;
  onStepClick?: (stepIndex: number) => void;
  orientation?: 'horizontal' | 'vertical';
}

const statusConfig = {
  pending: { color: 'bg-gray-300', icon: Clock },
  running: { color: 'bg-blue-500', icon: Loader },
  completed: { color: 'bg-green-500', icon: CheckCircle },
  error: { color: 'bg-red-500', icon: AlertCircle }
};

export function StepIndicator({
  steps,
  currentStep,
  onStepClick,
  orientation = 'horizontal'
}: StepIndicatorProps) {
  const isHorizontal = orientation === 'horizontal';

  return (
    <div className={cn(
      'flex',
      isHorizontal ? 'flex-row items-center' : 'flex-col'
    )}>
      {steps.map((step, index) => {
        const config = statusConfig[step.status];
        const StatusIcon = config.icon;
        const isActive = index === currentStep;
        const isClickable = onStepClick && !step.dependencies?.some(dep => 
          !steps.find(s => s.id === dep)?.status || steps.find(s => s.id === dep)?.status !== 'completed'
        );

        return (
          <div
            key={step.id}
            className={cn(
              'flex items-center',
              isHorizontal ? 'flex-row' : 'flex-col',
              isClickable && 'cursor-pointer'
            )}
            onClick={() => isClickable && onStepClick?.(index)}
          >
            {/* Step Circle */}
            <div className="relative">
              <div className={cn(
                'w-10 h-10 rounded-full flex items-center justify-center transition-all',
                config.color,
                isActive && 'ring-2 ring-blue-300 ring-offset-2',
                step.status === 'running' && 'animate-pulse'
              )}>
                <StatusIcon className="h-5 w-5 text-white" />
              </div>
              
              {isActive && (
                <div className="absolute inset-0 w-10 h-10 rounded-full bg-blue-500 opacity-20 animate-ping" />
              )}
            </div>

            {/* Step Label */}
            <div className={cn(
              'text-center',
              isHorizontal ? 'ml-3 mr-6' : 'mt-2 mb-4'
            )}>
              <div className={cn(
                'font-medium text-sm',
                isActive ? 'text-blue-600' : 'text-gray-700'
              )}>
                {step.title}
              </div>
              <div className="text-xs text-gray-500 max-w-[120px]">
                {step.description}
              </div>
            </div>

            {/* Connector Line */}
            {index < steps.length - 1 && (
              <div className={cn(
                'bg-gray-300',
                isHorizontal 
                  ? 'h-0.5 flex-1 -ml-6' 
                  : 'w-0.5 h-8 -mt-4 mx-auto'
              )} />
            )}
          </div>
        );
      })}
    </div>
  );
}
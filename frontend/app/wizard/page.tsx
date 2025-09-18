'use client';

import { useAppStore } from '@/stores/useAppStore';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Cog,
  Database,
  FlaskConical,
  FileText,
  CheckCircle,
  Rocket,
  LucideProps,
  HelpCircle,
  Server,
} from 'lucide-react';
import React from 'react';

// Icon mapping for steps
const stepIcons: { [key: string]: React.ComponentType<LucideProps> } = {
  setup: Server,
  questions: HelpCircle,
  'data-preprocessing': FlaskConical,
  'feature-engineering': Cog,
  'model-training': Rocket,
  'model-evaluation': CheckCircle,
  'model-deployment': Rocket,
};


export default function TrainingWizard() {
  const { trainingSteps } = useAppStore();

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">训练流程总览</h1>
        <p className="mt-2 text-lg text-gray-600 dark:text-gray-400">
          以下是完成模型训练所需的所有步骤。
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {trainingSteps.map((step, index) => {
          const Icon = stepIcons[step.id] || Cog;
          const isLocked = step.dependencies?.some(depId => 
            trainingSteps.find(s => s.id === depId)?.status !== 'completed'
          );

          return (
            <Card key={step.id} className="flex flex-col transition-all hover:shadow-lg">
              <CardHeader className="flex-row items-center gap-4">
                <div className="p-3 bg-primary/10 rounded-lg">
                  <Icon className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <CardTitle>{step.title}</CardTitle>
                  <CardDescription>步骤 {index + 1}</CardDescription>
                </div>
              </CardHeader>
              <CardContent className="flex-grow">
                <p className="text-sm text-muted-foreground">{step.description}</p>
              </CardContent>
              <CardFooter className="flex justify-between items-center bg-gray-50 dark:bg-gray-900/50 py-3 px-4 rounded-b-lg">
                <Badge variant={
                  step.status === 'completed' ? 'default' :
                  step.status === 'running' ? 'secondary' :
                  'outline'
                }>
                  {
                    step.status === 'completed' ? '已完成' :
                    step.status === 'running' ? '进行中' :
                    isLocked ? '已锁定' : '未开始'
                  }
                </Badge>
                <Button size="sm" variant="outline" disabled>
                  执行
                </Button>
              </CardFooter>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

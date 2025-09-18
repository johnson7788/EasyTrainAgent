'use client';

import { useAppStore } from '@/stores/useAppStore';
import { StepIndicator } from '@/components/ui/step-indicator';
import { TaskCard } from '@/components/ui/task-card';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { ChevronLeft, ChevronRight, PlayCircle } from 'lucide-react';
import { useState } from 'react';
import toast from 'react-hot-toast';

export default function TrainingWizard() {
  const { 
    trainingSteps, 
    currentStep, 
    setCurrentStep, 
    updateStepStatus, 
    addTask 
  } = useAppStore();

  const [isExecuting, setIsExecuting] = useState(false);
  
  const currentStepData = trainingSteps[currentStep];
  const totalSteps = trainingSteps.length;
  const completedSteps = trainingSteps.filter(step => step.status === 'completed').length;
  const progress = (completedSteps / totalSteps) * 100;

  const canExecuteStep = (step: typeof currentStepData) => {
    if (!step.dependencies) return true;
    return step.dependencies.every(depId => {
      const depStep = trainingSteps.find(s => s.id === depId);
      return depStep?.status === 'completed';
    });
  };

  const executeStep = async () => {
    if (!canExecuteStep(currentStepData)) {
      toast.error('请先完成前置步骤');
      return;
    }

    setIsExecuting(true);
    updateStepStatus(currentStepData.id, 'running');

    // 模拟执行任务
    const taskId = `task-${currentStepData.id}-${Date.now()}`;
    addTask({
      id: taskId,
      title: currentStepData.title,
      description: currentStepData.description,
      status: 'running',
      progress: 0
    });

    try {
      // 模拟执行过程
      for (let i = 0; i <= 100; i += 20) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        // updateTask(taskId, { progress: i });
      }

      updateStepStatus(currentStepData.id, 'completed');
      toast.success(`${currentStepData.title} 执行成功`);

      // 自动跳转到下一步
      if (currentStep < totalSteps - 1) {
        setTimeout(() => setCurrentStep(currentStep + 1), 1000);
      }
    } catch (error) {
      updateStepStatus(currentStepData.id, 'error');
      toast.error(`${currentStepData.title} 执行失败`);
    } finally {
      setIsExecuting(false);
    }
  };

  const nextStep = () => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const goToStep = (stepIndex: number) => {
    setCurrentStep(stepIndex);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">训练向导</h1>
        
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-gray-600">
              第 {currentStep + 1} 步 / 共 {totalSteps} 步
            </p>
            <div className="flex items-center gap-3">
              <Progress value={progress} className="w-64" />
              <span className="text-sm text-gray-500">{progress.toFixed(0)}%</span>
            </div>
          </div>
          
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              onClick={prevStep} 
              disabled={currentStep === 0}
            >
              <ChevronLeft className="h-4 w-4 mr-1" />
              上一步
            </Button>
            <Button 
              variant="outline" 
              onClick={nextStep} 
              disabled={currentStep === totalSteps - 1}
            >
              下一步
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      </div>

      {/* Step Indicator */}
      <Card>
        <CardHeader>
          <CardTitle>训练流程</CardTitle>
        </CardHeader>
        <CardContent>
          <StepIndicator 
            steps={trainingSteps}
            currentStep={currentStep}
            onStepClick={goToStep}
            orientation="horizontal"
          />
        </CardContent>
      </Card>

      {/* Current Step */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <TaskCard
            task={{
              id: currentStepData.id,
              title: currentStepData.title,
              description: currentStepData.description,
              status: currentStepData.status === 'completed' ? 'success' : 
                      currentStepData.status === 'running' ? 'running' : 'pending'
            }}
            onExecute={executeStep}
            showLogs={true}
          >
            {/* Step-specific content */}
            <div className="space-y-4">
              {currentStepData.id === 'setup' && (
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">
                    配置 MCP Server 连接，确保训练环境正常运行。
                  </p>
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <p className="text-sm text-blue-800">
                      💡 提示：请确保 MCP Server 已启动并监听正确的端口
                    </p>
                  </div>
                </div>
              )}

              {currentStepData.id === 'questions' && (
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">
                    生成用于训练的问题数据集，包括各种类型的问题和场景。
                  </p>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1">问题数量</label>
                      <input 
                        type="number" 
                        className="w-full px-3 py-2 border rounded-lg" 
                        defaultValue={1000}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">输出路径</label>
                      <input 
                        type="text" 
                        className="w-full px-3 py-2 border rounded-lg" 
                        defaultValue="./data/questions.json"
                      />
                    </div>
                  </div>
                </div>
              )}

              {!canExecuteStep(currentStepData) && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <p className="text-sm text-yellow-800">
                    ⚠️ 请先完成以下前置步骤：
                    {currentStepData.dependencies?.map(depId => {
                      const depStep = trainingSteps.find(s => s.id === depId);
                      return depStep ? ` "${depStep.title}"` : '';
                    }).join(', ')}
                  </p>
                </div>
              )}
            </div>
          </TaskCard>
        </div>

        <div className="space-y-6">
          {/* Step Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">当前步骤</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="font-medium">{currentStepData.title}</div>
                <div className="text-sm text-gray-600">{currentStepData.description}</div>
              </div>
              
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${
                  currentStepData.status === 'completed' ? 'bg-green-500' :
                  currentStepData.status === 'running' ? 'bg-blue-500 animate-pulse' :
                  currentStepData.status === 'error' ? 'bg-red-500' :
                  'bg-gray-400'
                }`} />
                <span className="text-sm capitalize">
                  {currentStepData.status === 'completed' ? '已完成' :
                   currentStepData.status === 'running' ? '运行中' :
                   currentStepData.status === 'error' ? '失败' : '等待中'}
                </span>
              </div>

              {canExecuteStep(currentStepData) && currentStepData.status === 'pending' && (
                <Button 
                  onClick={executeStep} 
                  disabled={isExecuting}
                  className="w-full"
                >
                  <PlayCircle className="h-4 w-4 mr-2" />
                  {isExecuting ? '执行中...' : '开始执行'}
                </Button>
              )}
            </CardContent>
          </Card>

          {/* Overall Progress */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">整体进度</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="text-2xl font-bold">{completedSteps}/{totalSteps}</div>
              <Progress value={progress} />
              <p className="text-sm text-gray-600">
                已完成 {completedSteps} 个步骤，还有 {totalSteps - completedSteps} 个步骤待执行
              </p>
            </CardContent>
          </Card>

          {/* Next Steps */}
          {currentStep < totalSteps - 1 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">下一步骤</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {trainingSteps.slice(currentStep + 1, currentStep + 3).map((step, index) => (
                    <div key={step.id} className="flex items-center gap-2 text-sm">
                      <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center text-xs">
                        {currentStep + index + 2}
                      </div>
                      <span>{step.title}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
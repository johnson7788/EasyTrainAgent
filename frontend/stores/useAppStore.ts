'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { TrainingStep, MCPConfig, LogEntry, Task } from '@/types';

interface AppStore {
  // Training Steps
  currentStep: number;
  trainingSteps: TrainingStep[];
  setCurrentStep: (step: number) => void;
  updateStepStatus: (stepId: string, status: TrainingStep['status']) => void;

  // MCP Configuration
  mcpConfig: MCPConfig;
  updateMCPConfig: (config: Partial<MCPConfig>) => void;

  // Tasks
  currentTasks: Task[];
  addTask: (task: Task) => void;
  updateTask: (taskId: string, updates: Partial<Task>) => void;
  removeTask: (taskId: string) => void;

  // Logs
  logs: LogEntry[];
  addLog: (log: Omit<LogEntry, 'id'>) => void;
  clearLogs: () => void;

  // UI State
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
}

const initialSteps: TrainingStep[] = [
  { id: 'setup', title: 'MCP 配置', description: '配置 MCP Server 连接', status: 'pending' },
  { id: 'questions', title: '问题生成', description: '生成训练问题数据', status: 'pending', dependencies: ['setup'] },
  { id: 'sft-data', title: 'SFT 数据', description: '生成监督微调训练数据', status: 'pending', dependencies: ['questions'] },
  { id: 'data-labeling', title: '数据标注', description: '人工审核和标注数据', status: 'pending', dependencies: ['sft-data'] },
  { id: 'sft-train', title: 'SFT 训练', description: '监督微调模型训练', status: 'pending', dependencies: ['data-labeling'] },
  { id: 'sft-eval', title: 'SFT 评估', description: '评估微调模型性能', status: 'pending', dependencies: ['sft-train'] },
  { id: 'rl-data', title: 'RL 数据准备', description: '准备强化学习数据', status: 'pending', dependencies: ['sft-eval'] },
  { id: 'rl-train', title: 'RL 训练', description: '强化学习模型训练', status: 'pending', dependencies: ['rl-data'] },
  { id: 'rl-eval', title: 'RL 评估', description: '评估强化学习模型', status: 'pending', dependencies: ['rl-train'] },
  { id: 'deploy', title: '模型部署', description: '部署训练好的模型', status: 'pending', dependencies: ['rl-eval'] },
  { id: 'test', title: '在线测试', description: '测试部署的模型服务', status: 'pending', dependencies: ['deploy'] }
];

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      // Training Steps
      currentStep: 0,
      trainingSteps: initialSteps,
      setCurrentStep: (step) => set({ currentStep: step }),
      updateStepStatus: (stepId, status) => set((state) => ({
        trainingSteps: state.trainingSteps.map(step =>
          step.id === stepId ? { ...step, status } : step
        )
      })),

      // MCP Configuration
      mcpConfig: {
        serverPath: '/path/to/mcp/server',
        isRunning: false,
        port: 8080
      },
      updateMCPConfig: (config) => set((state) => ({
        mcpConfig: { ...state.mcpConfig, ...config }
      })),

      // Tasks
      currentTasks: [],
      addTask: (task) => set((state) => ({
        currentTasks: [...state.currentTasks, task]
      })),
      updateTask: (taskId, updates) => set((state) => ({
        currentTasks: state.currentTasks.map(task =>
          task.id === taskId ? { ...task, ...updates } : task
        )
      })),
      removeTask: (taskId) => set((state) => ({
        currentTasks: state.currentTasks.filter(task => task.id !== taskId)
      })),

      // Logs
      logs: [],
      addLog: (log) => set((state) => ({
        logs: [{ ...log, id: Date.now().toString() }, ...state.logs].slice(0, 1000)
      })),
      clearLogs: () => set({ logs: [] }),

      // UI State
      sidebarCollapsed: false,
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }))
    }),
    {
      name: 'easytrain-storage',
      partialize: (state) => ({
        currentStep: state.currentStep,
        trainingSteps: state.trainingSteps,
        mcpConfig: state.mcpConfig
      })
    }
  )
);
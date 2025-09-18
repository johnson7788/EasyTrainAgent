export interface TrainingStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed' | 'failed';
  dependencies?: string[];
}

export interface MCPConfig {
  serverPath: string;
  isRunning: boolean;
  port: number;
  lastHealthCheck?: Date;
}

export interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'info' | 'warn' | 'error';
  message: string;
  source: string;
}

export interface Task {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'failed';
  progress?: number;
  createdAt: Date;
}

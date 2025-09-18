import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const source = searchParams.get('source');
  const level = searchParams.get('level');

  // 模拟日志数据
  const mockLogs = [
    {
      id: '1',
      timestamp: new Date(),
      level: 'info',
      message: 'MCP Server 启动成功',
      source: 'mcp-server'
    },
    {
      id: '2',
      timestamp: new Date(),
      level: 'debug',
      message: '正在加载模型配置...',
      source: 'model-loader'
    }
  ];

  return NextResponse.json(mockLogs);
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  
  // 这里可以实现日志存储逻辑
  console.log('New log entry:', body);
  
  return NextResponse.json({ success: true });
}
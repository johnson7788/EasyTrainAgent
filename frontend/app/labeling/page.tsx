"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { CheckCircle, XCircle, Upload, User, Bot, Wrench, Eye } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ConversationMessage {
  from: 'human' | 'gpt' | 'function_call' | 'observation';
  value: string;
}

interface Tool {
  name: string;
  description: string;
  parameters: {
    properties: Record<string, any>;
    required?: string[];
    type: string;
  };
}

interface ConversationData {
  conversations: ConversationMessage[];
  tools: Tool[];
}

const sampleData: ConversationData = {
  "conversations": [
    {"from": "human", "value": "今天的日期是什么？"},
    {"from": "function_call", "value": "{\"name\": \"get_current_date\", \"arguments\": {}}"},
    {"from": "observation", "value": "{\"result\": \"2025-09-17\"}"},
    {"from": "gpt", "value": "今天的日期是2025年9月17日。"}
  ],
  "tools": [
    {"name": "get_current_date", "description": "返回今天的日期，格式为YYYY-MM-DD。", "parameters": {"properties": {}, "type": "object"}},
    {"name": "set_seed", "description": "\n    设置全局 SEED，并重建最近30天的模拟数据。\n    返回生效的种子值。\n    ", "parameters": {"properties": {"seed": {"type": "integer"}}, "required": ["seed"], "type": "object"}},
    {"name": "regenerate_data", "description": "\n    手动重建模拟数据。\n    base_date: YYYY-MM-DD；若为空则使用今天。\n    days: 重建天数（含基准日）。\n    ", "parameters": {"properties": {"base_date": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": ""}, "days": {"default": 30, "type": "integer"}}, "type": "object"}},
    {"name": "get_auction_price", "description": "\n    获取指定省份在指定日期范围内的原料气竞拍价格（模拟）。\n    ", "parameters": {"properties": {"province": {"type": "string"}, "start_date": {"type": "string"}, "end_date": {"type": "string"}}, "required": ["province", "start_date", "end_date"], "type": "object"}},
    {"name": "get_factory_prices", "description": "\n    获取指定工厂列表在指定日期范围内的出厂价格（模拟）。\n    返回结构：{date: {factory: price, ...}, ...}\n    ", "parameters": {"properties": {"factory_names": {"items": {"type": "string"}, "type": "array"}, "start_date": {"type": "string"}, "end_date": {"type": "string"}}, "required": ["factory_names", "start_date", "end_date"], "type": "object"}},
    {"name": "get_lng_price", "description": "\n    获取指定地区从 start_date 到 end_date（默认今天）的每日 LNG 价格（模拟）。\n    - 基于月度基准价 + 小幅波动。\n    - 小幅波动由与 (region, start_date, end_date, 当天日期) 绑定的稳定 RNG 产生，\n      确保相同查询在不同时间点/调用次数下结果一致。\n    ", "parameters": {"properties": {"region": {"type": "string"}, "start_date": {"type": "string"}, "end_date": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": ""}}, "required": ["region", "start_date"], "type": "object"}}
  ]
};

export default function ConversationAnnotation() {
  const [data, setData] = useState<ConversationData>(sampleData);
  const [annotation, setAnnotation] = useState<'correct' | 'incorrect' | null>(null);
  const [notes, setNotes] = useState('');
  const [jsonInput, setJsonInput] = useState('');

  const getMessageIcon = (from: string) => {
    switch (from) {
      case 'human':
        return <User className="w-5 h-5" />;
      case 'gpt':
        return <Bot className="w-5 h-5" />;
      case 'function_call':
        return <Wrench className="w-5 h-5" />;
      case 'observation':
        return <Eye className="w-5 h-5" />;
      default:
        return <User className="w-5 h-5" />;
    }
  };

  const getMessageStyle = (from: string) => {
    switch (from) {
      case 'human':
        return 'bg-blue-50 border-blue-200 text-blue-900';
      case 'gpt':
        return 'bg-green-50 border-green-200 text-green-900';
      case 'function_call':
        return 'bg-purple-50 border-purple-200 text-purple-900';
      case 'observation':
        return 'bg-orange-50 border-orange-200 text-orange-900';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-900';
    }
  };

  const getMessageLabel = (from: string) => {
    switch (from) {
      case 'human':
        return '用户';
      case 'gpt':
        return 'AI助手';
      case 'function_call':
        return '函数调用';
      case 'observation':
        return '函数返回';
      default:
        return from;
    }
  };

  const handleLoadJson = () => {
    try {
      const parsed = JSON.parse(jsonInput);
      setData(parsed);
      setJsonInput('');
      setAnnotation(null);
      setNotes('');
    } catch (error) {
      alert('JSON格式错误，请检查数据格式');
    }
  };

  const formatJson = (value: string) => {
    try {
      const parsed = JSON.parse(value);
      return JSON.stringify(parsed, null, 2);
    } catch {
      return value;
    }
  };

  const handleSubmitAnnotation = () => {
    if (annotation) {
      console.log('标注结果:', {
        annotation,
        notes,
        timestamp: new Date().toISOString()
      });
      alert(`标注已提交: ${annotation === 'correct' ? '正确' : '错误'}${notes ? `\n备注: ${notes}` : ''}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            对话标注系统
          </h1>
          <p className="text-gray-600">
            为AI对话数据进行质量标注和评估
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Conversation Area */}
          <div className="lg:col-span-3 space-y-6">
            {/* JSON Input Section */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="w-5 h-5" />
                  加载对话数据
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Textarea
                    placeholder="粘贴JSON对话数据..."
                    value={jsonInput}
                    onChange={(e) => setJsonInput(e.target.value)}
                    className="h-32"
                  />
                  <Button onClick={handleLoadJson} className="w-full">
                    加载数据
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Conversation Display */}
            <Card>
              <CardHeader>
                <CardTitle>对话内容</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {data.conversations.map((message, index) => (
                    <div
                      key={index}
                      className={cn(
                        "border rounded-lg p-4 transition-all duration-200 hover:shadow-md",
                        getMessageStyle(message.from)
                      )}
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0">
                          {getMessageIcon(message.from)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="secondary">
                              {getMessageLabel(message.from)}
                            </Badge>
                            <span className="text-xs text-gray-500">
                              消息 #{index + 1}
                            </span>
                          </div>
                          <div className="font-mono text-sm">
                            {message.from === 'function_call' || message.from === 'observation' ? (
                              <pre className="whitespace-pre-wrap">
                                {formatJson(message.value)}
                              </pre>
                            ) : (
                              <p>{message.value}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Annotation Section */}
            <Card>
              <CardHeader>
                <CardTitle>标注评估</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex gap-4">
                    <Button
                      variant={annotation === 'correct' ? 'default' : 'outline'}
                      onClick={() => setAnnotation('correct')}
                      className="flex-1 h-12"
                    >
                      <CheckCircle className="w-5 h-5 mr-2" />
                      对话正常
                    </Button>
                    <Button
                      variant={annotation === 'incorrect' ? 'destructive' : 'outline'}
                      onClick={() => setAnnotation('incorrect')}
                      className="flex-1 h-12"
                    >
                      <XCircle className="w-5 h-5 mr-2" />
                      有错误
                    </Button>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      备注说明（可选）
                    </label>
                    <Textarea
                      placeholder="请描述发现的问题或补充说明..."
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      className="h-24"
                    />
                  </div>
                  
                  <Button 
                    onClick={handleSubmitAnnotation}
                    disabled={!annotation}
                    className="w-full h-12"
                  >
                    提交标注
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Tools Sidebar */}
          <div className="lg:col-span-1">
            <Card className="sticky top-4">
              <CardHeader>
                <CardTitle>可用工具</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {data.tools.map((tool, index) => (
                    <div
                      key={index}
                      className="border rounded-lg p-3 bg-white hover:shadow-sm transition-shadow"
                    >
                      <h4 className="font-semibold text-sm mb-2">
                        {tool.name}
                      </h4>
                      <p className="text-xs text-gray-600 mb-2 whitespace-pre-line">
                        {tool.description.trim()}
                      </p>
                      {tool.parameters.required && tool.parameters.required.length > 0 && (
                        <div className="text-xs">
                          <span className="text-gray-500">必需参数: </span>
                          <span className="font-mono text-blue-600">
                            {tool.parameters.required.join(', ')}
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
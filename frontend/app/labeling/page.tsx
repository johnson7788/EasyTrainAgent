'use client';

import { useState, useEffect } from 'react';
import { useAppStore } from '@/stores/useAppStore';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Loader2, Save, ChevronLeft, ChevronRight, User, Bot, Terminal, Microscope } from 'lucide-react';
import toast from 'react-hot-toast';

interface ConversationTurn {
  from: 'human' | 'function_call' | 'observation' | 'gpt';
  value: string | object;
  label?: {
    quality: number;
    comment: string;
  };
}

interface JsonlRecord {
  conversations: ConversationTurn[];
  tools?: any[];
}

export default function LabelingPage() {
  const { selectedJsonlFile } = useAppStore();
  const [records, setRecords] = useState<JsonlRecord[]>([]);
  const [labeledData, setLabeledData] = useState<JsonlRecord[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedJsonlFile) return;

    const loadFileContent = async () => {
      setIsLoading(true);
      setError(null);
      setRecords([]);
      setLabeledData([]);
      setCurrentIndex(0);

      try {
        const response = await fetch('/api/fs/read',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: selectedJsonlFile }),
          });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to read file.');
        }

        const data = await response.json();
        if (data.error) {
          throw new Error(data.error);
        }

        const lines = data.content.split('\n').filter(Boolean);
        const parsedRecords = lines.map((line: string) => JSON.parse(line));
        setRecords(parsedRecords);
        setLabeledData(JSON.parse(JSON.stringify(parsedRecords))); // Deep copy
      } catch (err: any) {
        setError(`Error loading file: ${err.message}`);
        toast.error(`Failed to load ${selectedJsonlFile}.`);
      } finally {
        setIsLoading(false);
      }
    };

    loadFileContent();
  }, [selectedJsonlFile]);

  const handleLabelChange = (turnIndex: number, quality: number, comment: string) => {
    const newLabeledData = [...labeledData];
    const recordToUpdate = newLabeledData[currentIndex];
    const turnToUpdate = recordToUpdate.conversations[turnIndex];

    if (turnToUpdate.from === 'gpt') {
      turnToUpdate.label = { quality, comment };
    }

    setLabeledData(newLabeledData);
  };

  const handleSave = async () => {
    if (!selectedJsonlFile) return;

    const contentToSave = labeledData.map(record => JSON.stringify(record)).join('\n');
    const originalFileName = selectedJsonlFile.split('/').pop() || 'data.jsonl';
    const newFileName = originalFileName.replace('.jsonl', '_labeled.jsonl');

    try {
      const response = await fetch('/api/fs/write',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path: newFileName, content: contentToSave }),
        });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to save file.');
      }

      toast.success(`Saved labeled data to ${newFileName}`);
    } catch (err: any) {
      setError(`Error saving file: ${err.message}`);
      toast.error(`Failed to save ${newFileName}.`);
    }
  };

  const goToNext = () => {
    if (currentIndex < records.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const goToPrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const getTurnIcon = (from: string) => {
    switch (from) {
      case 'human':
        return <User className="h-8 w-8 text-blue-500" />;
      case 'gpt':
        return <Bot className="h-8 w-8 text-green-500" />;
      case 'function_call':
        return <Terminal className="h-8 w-8 text-gray-500" />;
      case 'observation':
        return <Microscope className="h-8 w-8 text-purple-500" />;
      default:
        return null;
    }
  };

  const getTurnStyle = (from: string) => {
    switch (from) {
      case 'human':
        return 'bg-blue-50 text-blue-900';
      case 'gpt':
        return 'bg-green-50 text-green-900';
      case 'function_call':
        return 'bg-gray-100 text-gray-800';
      case 'observation':
        return 'bg-purple-50 text-purple-900';
      default:
        return 'bg-gray-50 text-gray-900';
    }
  };

  if (!selectedJsonlFile) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        Select a .jsonl file to start labeling.
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full text-red-500">
        {error}
      </div>
    );
  }

  const currentRecord = labeledData[currentIndex];
  const labeledCount = labeledData.filter(r => 
    r.conversations.some(t => t.from === 'gpt' && t.label)
  ).length;
  const progress = (labeledCount / records.length) * 100;

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle>Labeling: {selectedJsonlFile}</CardTitle>
          <div className="text-sm text-gray-500">
            Record {currentIndex + 1} of {records.length}
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-grow overflow-auto p-4 space-y-4">
        {currentRecord?.conversations.map((turn, turnIndex) => (
          <div key={turnIndex} className={`flex items-start gap-3`}>
            {getTurnIcon(turn.from)}
            <div className={`p-3 rounded-lg max-w-[80%] ${getTurnStyle(turn.from)}`}>
              <pre className="text-sm whitespace-pre-wrap">{typeof turn.value === 'string' ? turn.value : JSON.stringify(turn.value, null, 2)}</pre>
              {turn.from === 'gpt' && (
                <div className="mt-4 space-y-2">
                  <div>
                    <label className="text-xs font-medium">Quality (1-5)</label>
                    <div className="flex gap-1 mt-1">
                      {[1, 2, 3, 4, 5].map(q => (
                        <Button
                          key={q}
                          size="sm"
                          variant={turn.label?.quality === q ? 'default' : 'outline'}
                          onClick={() => handleLabelChange(turnIndex, q, turn.label?.comment || '')}
                        >
                          {q}
                        </Button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="text-xs font-medium">Comment</label>
                    <Textarea
                      placeholder="Add a comment..."
                      className="mt-1 text-sm"
                      value={turn.label?.comment || ''}
                      onChange={(e) => handleLabelChange(turnIndex, turn.label?.quality || 0, e.target.value)}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </CardContent>
      <CardFooter className="flex flex-col gap-4">
        <div className="w-full">
          <Progress value={progress} />
          <div className="text-xs text-gray-500 mt-1 text-center">
            {labeledCount} / {records.length} labeled
          </div>
        </div>
        <div className="flex justify-between w-full">
          <Button variant="outline" onClick={goToPrevious} disabled={currentIndex === 0}>
            <ChevronLeft className="h-4 w-4 mr-2" /> Previous
          </Button>
          <Button onClick={handleSave}>
            <Save className="h-4 w-4 mr-2" /> Save
          </Button>
          <Button variant="outline" onClick={goToNext} disabled={currentIndex === records.length - 1}>
            Next <ChevronRight className="h-4 w-4 ml-2" />
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
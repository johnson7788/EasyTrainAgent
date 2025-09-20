'use client';

import { useState, useEffect } from 'react';
import { useAppStore } from '@/stores/useAppStore';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Loader2, Save, ChevronLeft, ChevronRight, User, Bot, Terminal, Microscope, Check, X } from 'lucide-react';
import toast from 'react-hot-toast';

interface ConversationTurn {
  from: 'human' | 'function_call' | 'observation' | 'gpt';
  value: string | object;
  label?: {
    status: 'correct' | 'incorrect';
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

  const handleLabelChange = (turnIndex: number, status: 'correct' | 'incorrect', comment: string) => {
    const newLabeledData = [...labeledData];
    const recordToUpdate = newLabeledData[currentIndex];
    const turnToUpdate = recordToUpdate.conversations[turnIndex];

    if (turnToUpdate.from === 'gpt') {
      if (turnToUpdate.label?.status === status) {
        delete turnToUpdate.label;
      } else {
        turnToUpdate.label = { status, comment };
      }
    }

    setLabeledData(newLabeledData);
  };

  const handleCommentChange = (turnIndex: number, comment: string) => {
    const newLabeledData = [...labeledData];
    const recordToUpdate = newLabeledData[currentIndex];
    const turnToUpdate = recordToUpdate.conversations[turnIndex];

    if (turnToUpdate.from === 'gpt' && turnToUpdate.label) {
      turnToUpdate.label.comment = comment;
      setLabeledData(newLabeledData);
    }
  };

  const handleSave = async () => {
    if (!selectedJsonlFile) return;

    const correctRecords: JsonlRecord[] = [];
    const wrongRecords: JsonlRecord[] = [];

    labeledData.forEach(record => {
      const gptTurns = record.conversations.filter(t => t.from === 'gpt');
      if (gptTurns.length === 0 || gptTurns.some(t => !t.label)) {
        return; // Skip unlabeled records
      }

      if (gptTurns.some(t => t.label?.status === 'incorrect')) {
        wrongRecords.push(record);
      } else {
        correctRecords.push(record);
      }
    });

    const dir = selectedJsonlFile.substring(0, selectedJsonlFile.lastIndexOf('/'));
    const originalFileName = selectedJsonlFile.substring(selectedJsonlFile.lastIndexOf('/') + 1).replace('.jsonl', '');
    
    const savePromises = [];

    if (correctRecords.length > 0) {
      const correctFilePath = `${dir}/${originalFileName}_correct.jsonl`;
      const correctContent = correctRecords.map(r => JSON.stringify(r)).join('\n');
      savePromises.push(
        fetch('/api/fs/write', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path: correctFilePath, content: correctContent }),
        }).then(async (res) => {
          if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.error || `Failed to save ${correctFilePath}`);
          }
          return correctFilePath.split('/').pop();
        })
      );
    }

    if (wrongRecords.length > 0) {
      const wrongFilePath = `${dir}/${originalFileName}_wrong.jsonl`;
      const wrongContent = wrongRecords.map(r => JSON.stringify(r)).join('\n');
      savePromises.push(
        fetch('/api/fs/write', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path: wrongFilePath, content: wrongContent }),
        }).then(async (res) => {
          if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.error || `Failed to save ${wrongFilePath}`);
          }
          return wrongFilePath.split('/').pop();
        })
      );
    }

    if (savePromises.length === 0) {
      toast('No fully labeled records to save.');
      return;
    }

    try {
      const savedFiles = await Promise.all(savePromises);
      toast.success(`Saved: ${savedFiles.join(', ')}`);
    } catch (err: any) {
      setError(`Error saving files: ${err.message}`);
      toast.error(err.message);
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
    r.conversations.filter(t => t.from === 'gpt').every(t => t.label)
  ).length;
  const progress = records.length > 0 ? (labeledCount / records.length) * 100 : 0;

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle>Labeling: {selectedJsonlFile.split('/').pop()}</CardTitle>
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
                    <label className="text-xs font-medium">Label</label>
                    <div className="flex gap-2 mt-1">
                        <Button
                          size="sm"
                          variant={turn.label?.status === 'correct' ? 'default' : 'outline'}
                          className="text-green-600 border-green-600 hover:bg-green-100"
                          onClick={() => handleLabelChange(turnIndex, 'correct', turn.label?.comment || '')}
                        >
                          <Check className="h-4 w-4 mr-2" /> Correct
                        </Button>
                        <Button
                          size="sm"
                          variant={turn.label?.status === 'incorrect' ? 'destructive' : 'outline'}
                          className={turn.label?.status !== 'incorrect' ? "text-red-600 border-red-600 hover:bg-red-100" : ""}
                          onClick={() => handleLabelChange(turnIndex, 'incorrect', turn.label?.comment || '')}
                        >
                          <X className="h-4 w-4 mr-2" /> Incorrect
                        </Button>
                    </div>
                  </div>
                  <div>
                    <label className="text-xs font-medium">Comment</label>
                    <Textarea
                      placeholder="Add a comment..."
                      className="mt-1 text-sm"
                      value={turn.label?.comment || ''}
                      onChange={(e) => handleCommentChange(turnIndex, e.target.value)}
                      disabled={!turn.label}
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
            {labeledCount} / {records.length} records fully labeled
          </div>
        </div>
        <div className="flex justify-between w-full">
          <Button variant="outline" onClick={goToPrevious} disabled={currentIndex === 0}>
            <ChevronLeft className="h-4 w-4 mr-2" /> Previous
          </Button>
          <Button onClick={handleSave}>
            <Save className="h-4 w-4 mr-2" /> Save Labeled Data
          </Button>
          <Button variant="outline" onClick={goToNext} disabled={currentIndex === records.length - 1}>
            Next <ChevronRight className="h-4 w-4 ml-2" />
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}

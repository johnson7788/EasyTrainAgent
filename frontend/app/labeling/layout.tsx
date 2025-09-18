'use client';

import React, { useState, useEffect } from 'react';
import { useAppStore } from '@/stores/useAppStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, File } from 'lucide-react';
import toast from 'react-hot-toast';

export default function LabelingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { setSelectedJsonlFile, clearSelectedJsonlFile } = useAppStore();
  const [jsonlFiles, setJsonlFiles] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  useEffect(() => {
    const fetchJsonlFiles = async () => {
      setIsLoading(true);
      try {
        const response = await fetch('/api/run/cmd', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ cmd: ['find', '.', '-name', '*.jsonl'] }),
        });

        const data = await response.json();

        if (!response.ok || !data.ok) {
          const errorMsg = data.stderr_b64
            ? atob(data.stderr_b64)
            : data.error || 'Failed to fetch .jsonl files.';
          throw new Error(errorMsg);
        }

        if (data.stderr_b64) {
          const errorMsg = atob(data.stderr_b64);
          if (errorMsg) {
            throw new Error(errorMsg);
          }
        }

        const decodedStdout = atob(data.stdout_b64);
        const files = decodedStdout.split('\n').filter(Boolean);
        setJsonlFiles(files);
      } catch (error: any) {
        console.error(error);
        toast.error(`Failed to load .jsonl files: ${error.message}`);
      } finally {
        setIsLoading(false);
      }
    };
    fetchJsonlFiles();

    return () => {
      clearSelectedJsonlFile();
    };
  }, [clearSelectedJsonlFile]);

  const handleFileSelect = (fileName: string) => {
    setSelectedFile(fileName);
    setSelectedJsonlFile(fileName);
  };

  return (
    <div className="p-6 grid grid-cols-1 md:grid-cols-4 gap-6">
      <div className="md:col-span-1">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <File className="h-5 w-5" />
              <span>JSONL Files</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center gap-2 text-gray-500">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Loading...</span>
              </div>
            ) : jsonlFiles.length > 0 ? (
              <div className="space-y-2">
                {jsonlFiles.map((file) => (
                  <Button
                    key={file}
                    variant={selectedFile === file ? 'default' : 'outline'}
                    onClick={() => handleFileSelect(file)}
                    className="w-full justify-start text-left"
                  >
                    {file}
                  </Button>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No .jsonl files found.</p>
            )}
          </CardContent>
        </Card>
      </div>
      <div className="md:col-span-3">{children}</div>
    </div>
  );
}

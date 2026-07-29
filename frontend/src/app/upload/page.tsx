"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { uploadDataset } from "@/services/dataset";
import { runPipeline } from "@/services/job";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { UploadCloud, File, AlertCircle } from "lucide-react";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ui/use-toast"; // assuming standard shadcn hook structure
import { CopilotDrawer } from "@/components/copilot/CopilotDrawer";

export default function UploadPage() {
  const router = useRouter();
  const { toast } = useToast();
  
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewStats, setPreviewStats] = useState<{name: string, size: string} | null>(null);

  const [datasetId, setDatasetId] = useState<string | null>(null);

  const uploadMutation = useMutation({
    mutationFn: uploadDataset,
    onSuccess: (data) => {
      setDatasetId(data.dataset_id);
      toast({
        title: "Dataset uploaded",
        description: "Successfully saved. You can now use the Copilot to analyze it.",
      });
    },
    onError: (error: any) => {
      toast({
        variant: "destructive",
        title: "Upload Failed",
        description: error.response?.data?.detail || "An error occurred during upload.",
      });
    }
  });

  const pipelineMutation = useMutation({
    mutationFn: (dataset_id: string) => runPipeline({ 
        dataset_id, 
        pipeline: { validation: true, cleaning: true, feature_engineering: true, feature_selection: true, visualization: true, reports: true }
    }),
    onSuccess: (data) => {
      localStorage.setItem("active_job_id", data.job_id);
      router.push(`/jobs/${data.job_id}/processing`);
    },
    onError: () => {
      toast({
        variant: "destructive",
        title: "Pipeline Start Failed",
        description: "Failed to queue pipeline execution.",
      });
    }
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      if (!file.name.endsWith(".csv")) {
          toast({ variant: "destructive", title: "Invalid file", description: "Please select a .csv file" });
          return;
      }
      setSelectedFile(file);
      setPreviewStats({
          name: file.name,
          size: (file.size / 1024 / 1024).toFixed(2) + " MB"
      });
    }
  };

  const handleUpload = () => {
    if (selectedFile) {
      uploadMutation.mutate(selectedFile);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Upload Dataset</h1>
        <p className="text-zinc-500">Submit a CSV dataset to initiate the deterministic Analytics Engine.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Select File</CardTitle>
          <CardDescription>Drag and drop your dataset here, or click to browse.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
            
          <div className="border-2 border-dashed border-zinc-300 dark:border-zinc-700 rounded-lg p-12 text-center hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors relative">
            <input 
              type="file" 
              accept=".csv" 
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
              onChange={handleFileChange}
            />
            <div className="flex flex-col items-center gap-2 text-zinc-500">
              <UploadCloud className="w-10 h-10 mb-2" />
              <p className="font-medium">Click or drag CSV file to this area to upload</p>
              <p className="text-sm">Maximum file size 500MB</p>
            </div>
          </div>

          {previewStats && (
            <div className="bg-zinc-50 dark:bg-zinc-900 p-4 rounded-lg flex items-center gap-4 border">
              <div className="p-2 bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400 rounded">
                <File className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <p className="font-semibold">{previewStats.name}</p>
                <p className="text-sm text-zinc-500">{previewStats.size}</p>
              </div>
            </div>
          )}

          {!datasetId ? (
            <Button 
              className="w-full h-12 text-lg font-medium" 
              disabled={!selectedFile || uploadMutation.isPending || pipelineMutation.isPending}
              onClick={handleUpload}
            >
              {uploadMutation.isPending ? "Uploading..." : "Upload Dataset"}
            </Button>
          ) : (
            <div className="flex flex-col gap-4">
              <CopilotDrawer jobId={datasetId} />
              <Button 
                variant="outline"
                className="w-full" 
                onClick={() => pipelineMutation.mutate(datasetId)}
                disabled={pipelineMutation.isPending}
              >
                Or Run Default Pipeline Directly
              </Button>
            </div>
          )}

        </CardContent>
      </Card>
    </div>
  );
}

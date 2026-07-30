"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useMutation, useQuery } from "@tanstack/react-query";
import { startAutoML, getAutoMLStatus, getAutoMLReport } from "@/services/automl";
import { useToast } from "@/components/ui/use-toast";
import { Play, Loader2, Trophy, Clock, CheckCircle2, AlertTriangle, FileText } from "lucide-react";
import ReactMarkdown from "react-markdown";

export function AutoMLDashboard({ jobId }: { jobId: string }) {
  const { toast } = useToast();
  
  // Status Polling
  const { data: statusData, refetch: refetchStatus } = useQuery({
    queryKey: ["automlStatus", jobId],
    queryFn: () => getAutoMLStatus(jobId),
    refetchInterval: (query) => {
        const state = query.state?.data?.status;
        if (state === "COMPLETED" || state === "FAILED") return false;
        return 1000;
    }
  });

  // Report fetching (only when completed)
  const { data: reportData } = useQuery({
    queryKey: ["automlReport", jobId],
    queryFn: () => getAutoMLReport(jobId),
    enabled: statusData?.status === "COMPLETED"
  });

  const startMutation = useMutation({
    mutationFn: (targetColumn?: string) => startAutoML({ job_id: jobId, target_column: targetColumn }),
    onSuccess: () => {
      toast({ title: "AutoML Started", description: "The execution manifest has been dispatched." });
      refetchStatus();
    },
    onError: (err: any) => {
      toast({ title: "Error", description: err.message, variant: "destructive" });
    }
  });

  const handleStart = () => {
    const targetColumn = localStorage.getItem(`target_column_${jobId}`) || undefined;
    startMutation.mutate(targetColumn);
  };

  const isRunning = statusData?.status === "RUNNING";
  const isCompleted = statusData?.status === "COMPLETED";
  const isFailed = statusData?.status === "FAILED";

  return (
    <div className="space-y-6">
      
      {/* Header & Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Model Training & AutoML Orchestrator
          </CardTitle>
          <CardDescription>
            Executes the deterministic Training Plan via parallel candidate training and hyperparameter search.
          </CardDescription>
        </CardHeader>
        <CardContent>
            {!isRunning && !isCompleted && !isFailed && (
                <Button onClick={handleStart} disabled={startMutation.isPending} className="bg-indigo-600 hover:bg-indigo-700 text-white">
                    {startMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
                    Start AutoML Session
                </Button>
            )}

            {isRunning && (
                <div className="flex flex-col items-center justify-center p-8 space-y-4 bg-indigo-50 dark:bg-indigo-950/30 rounded-lg border border-indigo-100 dark:border-indigo-900">
                    <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
                    <h3 className="font-semibold text-lg text-indigo-900 dark:text-indigo-200">Training Session in Progress</h3>
                    <p className="text-sm text-indigo-600 dark:text-indigo-400">Dispatching candidate models across worker pool...</p>
                </div>
            )}

            {isFailed && (
                <div className="p-4 bg-red-50 text-red-700 rounded-lg flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5" />
                    <span>AutoML Session Failed: {statusData.error}</span>
                </div>
            )}
        </CardContent>
      </Card>

      {/* Results / Leaderboard */}
      {isCompleted && statusData?.leaderboard && (
          <Card>
              <CardHeader>
                  <CardTitle className="flex items-center gap-2"><Trophy className="w-5 h-5 text-amber-500" /> Leaderboard</CardTitle>
              </CardHeader>
              <CardContent>
                  <div className="space-y-3">
                      {statusData.leaderboard.map((model: any, idx: number) => (
                          <div key={model.model_id} className={`p-4 rounded-lg border flex items-center justify-between ${idx === 0 ? 'bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800' : 'bg-zinc-50 dark:bg-zinc-900'}`}>
                              <div className="flex items-center gap-4">
                                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${idx === 0 ? 'bg-amber-500 text-white' : 'bg-zinc-200 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400'}`}>
                                      {idx + 1}
                                  </div>
                                  <div>
                                      <h4 className="font-bold text-lg">{model.model_name}</h4>
                                      <div className="text-xs text-zinc-500 mt-1">
                                        <span className="flex items-center gap-1"><Clock className="w-3 h-3"/> {model.training_time_sec.toFixed(2)}s</span>
                                      </div>
                                  </div>
                              </div>
                              <div className="text-right">
                                  {Object.entries(model.metrics).slice(0, 3).map(([key, val]: any) => (
                                      <div key={key} className="text-sm">
                                          <span className="uppercase text-zinc-500 mr-2">{key}:</span>
                                          <span className="font-mono font-medium">{val.toFixed(4)}</span>
                                      </div>
                                  ))}
                              </div>
                          </div>
                      ))}
                  </div>
              </CardContent>
          </Card>
      )}

      {/* Full Report Markdown */}
      {isCompleted && reportData?.report_markdown && (
          <Card>
              <CardHeader>
                  <CardTitle className="flex items-center gap-2"><FileText className="w-5 h-5 text-blue-500" /> AutoML Execution Report</CardTitle>
              </CardHeader>
              <CardContent className="prose dark:prose-invert max-w-none whitespace-pre-line">
                  <ReactMarkdown>{reportData.report_markdown}</ReactMarkdown>
              </CardContent>
          </Card>
      )}

    </div>
  );
}

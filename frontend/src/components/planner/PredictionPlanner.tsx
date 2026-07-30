"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useMutation, useQuery } from "@tanstack/react-query";
import { 
  getTargetCandidates, 
  generateTrainingPlan, 
  PlannerRequest 
} from "@/services/planner";
import { useToast } from "@/components/ui/use-toast";
import { ArrowRight, CheckCircle2, Download, AlertTriangle, Target, BrainCircuit, Activity, LineChart, FileJson } from "lucide-react";

export function PredictionPlanner({ jobId, onProceed }: { jobId: string, onProceed?: () => void }) {
  const { toast } = useToast();
  const [selectedTarget, setSelectedTarget] = useState<string | null>(null);
  const [trainingPlan, setTrainingPlan] = useState<any>(null);

  // 1. Fetch Target Candidates
  const { data: targetData, isLoading: loadingTargets } = useQuery({
    queryKey: ["targetCandidates", jobId],
    queryFn: () => getTargetCandidates({ job_id: jobId }),
  });

  // 2. Generate Training Plan once target is confirmed
  const generatePlanMutation = useMutation({
    mutationFn: (target: string) => generateTrainingPlan({ job_id: jobId, target_column: target }),
    onSuccess: (data) => {
      setTrainingPlan(data);
      toast({ title: "Training Plan Generated", description: "Successfully generated deterministic ML plan." });
    },
    onError: (err: any) => {
      toast({ title: "Planner Error", description: err.message, variant: "destructive" });
    }
  });

  const handleConfirmTarget = (target: string) => {
    setSelectedTarget(target);
    localStorage.setItem(`target_column_${jobId}`, target);
    generatePlanMutation.mutate(target);
  };

  const handleExportPlan = () => {
    if (!trainingPlan) return;
    const blob = new Blob([JSON.stringify(trainingPlan, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `training_plan_${jobId}.json`;
    a.click();
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BrainCircuit className="w-5 h-5 text-indigo-600" />
          Prediction Planner
        </CardTitle>
        <CardDescription>
          Deterministically analyze dataset readiness and orchestrate inputs for AutoML.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        
        {/* Step 1: Target Selection */}
        <div className="space-y-4">
          <h3 className="font-semibold flex items-center gap-2"><Target className="w-4 h-4"/> 1. Target Detection & Confirmation</h3>
          
          {!selectedTarget && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {loadingTargets ? (
                <div className="text-zinc-500 text-sm">Scanning columns...</div>
              ) : targetData?.candidates?.length > 0 ? (
                targetData.candidates.map((c: any) => (
                  <div key={c.column} className="border p-4 rounded-lg bg-zinc-50 dark:bg-zinc-900 flex justify-between items-center">
                    <div>
                      <p className="font-bold">{c.column}</p>
                      <p className="text-xs text-zinc-500">Predicted Task: {c.predicted_task} ({(c.confidence * 100).toFixed(0)}% Conf)</p>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => handleConfirmTarget(c.column)}>
                      Confirm
                    </Button>
                  </div>
                ))
              ) : (
                <div className="text-zinc-500 text-sm">No clear targets detected. Please ensure your dataset has a label column.</div>
              )}
            </div>
          )}

          {selectedTarget && (
            <div className="bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 p-3 rounded-lg flex items-center gap-2 border border-green-200 dark:border-green-800">
              <CheckCircle2 className="w-5 h-5" />
              <span>Target Confirmed: <strong>{selectedTarget}</strong></span>
              <Button variant="link" size="sm" className="ml-auto p-0 h-auto text-green-700 dark:text-green-400" onClick={() => {
                setSelectedTarget(null);
                setTrainingPlan(null);
              }}>Change</Button>
            </div>
          )}
        </div>

        {/* Step 2: Planning Results */}
        {generatePlanMutation.isPending && (
          <div className="py-8 text-center text-zinc-500 animate-pulse flex flex-col items-center">
            <Activity className="w-6 h-6 mb-2" />
            Generating deterministic training plan...
          </div>
        )}

        {trainingPlan && (
          <div className="space-y-6 border-t pt-6 mt-6">
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-zinc-50 dark:bg-zinc-900 p-4 rounded-lg border">
                <p className="text-xs text-zinc-500 uppercase font-bold tracking-wider mb-1">Detected Task</p>
                <p className="text-lg font-semibold flex items-center gap-2">
                  {trainingPlan.configuration.task}
                </p>
              </div>
              <div className={`p-4 rounded-lg border ${trainingPlan.configuration.readiness.is_ready ? 'bg-green-50 dark:bg-green-900/20 border-green-200' : 'bg-red-50 dark:bg-red-900/20 border-red-200'}`}>
                <p className="text-xs uppercase font-bold tracking-wider mb-1">ML Readiness Score</p>
                <p className="text-lg font-semibold flex items-center gap-2">
                  {trainingPlan.configuration.readiness.readiness_score} / 100
                  {!trainingPlan.configuration.readiness.is_ready && <AlertTriangle className="w-4 h-4 text-red-500"/>}
                </p>
              </div>
              <div className="bg-zinc-50 dark:bg-zinc-900 p-4 rounded-lg border">
                <p className="text-xs text-zinc-500 uppercase font-bold tracking-wider mb-1">Evaluation Metric</p>
                <p className="text-lg font-semibold flex items-center gap-2">
                  {trainingPlan.configuration.evaluation_strategy.metrics[0]}
                </p>
              </div>
            </div>

            {/* Issues */}
            {trainingPlan.configuration.readiness.issues.length > 0 && (
              <div className="bg-amber-50 dark:bg-amber-950/30 p-4 rounded-lg border border-amber-200 dark:border-amber-900">
                <h4 className="text-amber-800 dark:text-amber-300 font-semibold mb-2 flex items-center gap-2"><AlertTriangle className="w-4 h-4"/> Readiness Issues Detected</h4>
                <ul className="list-disc pl-5 text-sm text-amber-700 dark:text-amber-400 space-y-1">
                  {trainingPlan.configuration.readiness.issues.map((issue: string, idx: number) => (
                    <li key={idx}>{issue}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Model Recommendations */}
            <div>
              <h4 className="font-semibold flex items-center gap-2 mb-3"><LineChart className="w-4 h-4"/> Recommended Models</h4>
              <div className="space-y-3">
                {trainingPlan.configuration.recommended_models.map((model: any, idx: number) => (
                  <div key={model.model_id} className="border p-3 rounded-lg flex items-center justify-between">
                    <div>
                      <p className="font-bold flex items-center gap-2">
                        {idx + 1}. {model.model_name} 
                        <span className="text-xs font-normal px-2 py-0.5 bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300 rounded-full">Score: {model.suitability_score}</span>
                      </p>
                      <p className="text-xs text-zinc-500 mt-1">Cost: {model.computational_cost} | Interpretability: {model.interpretability}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4 pt-4 border-t">
              <Button onClick={handleExportPlan} className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white">
                <FileJson className="w-4 h-4 mr-2" /> Export Training Plan
              </Button>
              <Button onClick={onProceed} className="flex-1 bg-zinc-900 hover:bg-zinc-800 text-white dark:bg-zinc-50 dark:hover:bg-zinc-200 dark:text-zinc-950 font-medium">
                Proceed to AutoML <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

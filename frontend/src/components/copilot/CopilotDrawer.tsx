"use client";

import { useState } from "react";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Bot, Sparkles, AlertCircle, Play } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { understandDataset, suggestPipeline, interactiveTransform, CopilotRequestPayload } from "@/services/copilot";
import { runPipeline } from "@/services/job";
import { useToast } from "@/components/ui/use-toast";
import ReactMarkdown from "react-markdown";

export function CopilotDrawer({ jobId }: { jobId: string }) {
  const [insight, setInsight] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [intent, setIntent] = useState("");
  const { toast } = useToast();

  const handleUnderstand = async () => {
    setLoading(true);
    setInsight(null);
    try {
      const data = await understandDataset({ job_id: jobId });
      setInsight({ type: "understanding", data });
    } catch (err: any) {
      toast({ title: "Copilot Error", description: err.message, variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const handleSuggest = async () => {
    setLoading(true);
    setInsight(null);
    try {
      const data = await suggestPipeline({ job_id: jobId });
      setInsight({ type: "suggestion", data });
    } catch (err: any) {
      toast({ title: "Copilot Error", description: err.message, variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const handleTransform = async () => {
    if (!intent) return;
    setLoading(true);
    setInsight(null);
    try {
      // In a real app we'd resolve actual dataset paths from job metadata
      const payload = {
        job_id: jobId,
        user_intent: intent,
        dataset_path: "data/sample_input/dataset.xlsx",
        output_path: "data/processed/output.xlsx"
      };
      const data = await interactiveTransform(payload);
      setInsight({ type: "transform", data });
      toast({ title: "Transformation Applied", description: "Dataset has been successfully modified." });
    } catch (err: any) {
      toast({ title: "Execution Failed", description: err.message, variant: "destructive" });
    } finally {
      setLoading(false);
      setIntent("");
    }
  };

  const executePipelineMutation = useMutation({
    mutationFn: runPipeline,
    onSuccess: () => {
      toast({ title: "Pipeline Started", description: "Copilot suggested pipeline is now executing." });
      // In a real app we'd redirect or refresh
      window.location.href = `/jobs/${jobId}/processing`;
    },
    onError: (err: any) => {
      toast({ title: "Execution Failed", description: err.message, variant: "destructive" });
    }
  });

  return (
    <Sheet>
      <SheetTrigger
        render={
          <Button variant="outline" className="w-full h-11 gap-2 bg-indigo-50/50 dark:bg-indigo-950/20 text-indigo-700 dark:text-indigo-400 border-indigo-200 dark:border-indigo-800">
            <Bot className="w-4 h-4" /> Analyze with AI Copilot
          </Button>
        }
      />
      <SheetContent className="w-[400px] sm:w-[540px] overflow-y-auto">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            Intelligent Copilot
          </SheetTitle>
          <SheetDescription>
            Context-aware AI insights powered by deterministic Analytics Engine metadata.
          </SheetDescription>
        </SheetHeader>

        <div className="grid grid-cols-2 gap-2 mt-6">
          <Button variant="outline" onClick={handleUnderstand} disabled={loading}>
            Understand Dataset
          </Button>
          <Button variant="outline" onClick={handleSuggest} disabled={loading}>
            Suggest Pipeline
          </Button>
        </div>

        <div className="mt-4 flex gap-2">
          <input 
            type="text"
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            placeholder="E.g., Pivot plant data based on variable column" 
            value={intent}
            onChange={(e) => setIntent(e.target.value)}
            disabled={loading}
          />
          <Button variant="default" onClick={handleTransform} disabled={loading || !intent}>
            Apply Transform
          </Button>
        </div>

        <div className="mt-8 space-y-4">
          {loading && (
            <div className="flex items-center justify-center p-8 text-zinc-500">
              <Sparkles className="w-6 h-6 animate-pulse mr-2" />
              Generating insights...
            </div>
          )}

          {insight?.type === "understanding" && (
            <div className="space-y-4 p-4 bg-zinc-50 dark:bg-zinc-900 rounded-lg border">
              <h3 className="font-bold text-lg">{insight.data.title}</h3>
              <p className="text-zinc-700 dark:text-zinc-300">{insight.data.summary}</p>
              
              <div className="space-y-2">
                <h4 className="font-semibold text-sm text-zinc-500 uppercase tracking-wider">Recommendations</h4>
                <ul className="list-disc pl-5 space-y-1 text-sm">
                  {insight.data.recommendations.map((rec: string, i: number) => (
                    <li key={i}>{rec}</li>
                  ))}
                </ul>
              </div>

              <div className="text-xs text-zinc-400 mt-4 pt-4 border-t flex justify-between">
                <span>Confidence: {(insight.data.confidence * 100).toFixed(0)}%</span>
                <span>Sources: {insight.data.references.join(", ")}</span>
              </div>
            </div>
          )}

          {insight?.type === "suggestion" && (
            <div className="space-y-4 p-4 bg-zinc-50 dark:bg-zinc-900 rounded-lg border">
              <h3 className="font-bold text-lg">{insight.data.name}</h3>
              
              <div className="space-y-2">
                <h4 className="font-semibold text-sm text-zinc-500 uppercase tracking-wider">Reasoning</h4>
                <ul className="list-disc pl-5 space-y-1 text-sm">
                  {insight.data.reasoning.map((reason: string, i: number) => (
                    <li key={i}>{reason}</li>
                  ))}
                </ul>
              </div>

              <div className="bg-indigo-50 dark:bg-indigo-900/20 p-4 rounded-md border border-indigo-100 dark:border-indigo-900 mt-4">
                <h4 className="font-semibold text-indigo-800 dark:text-indigo-300 mb-2">Configuration</h4>
                <pre className="text-xs text-indigo-700 dark:text-indigo-400 overflow-x-auto">
                  {JSON.stringify(insight.data.steps, null, 2)}
                </pre>
              </div>

              <Button 
                className="w-full mt-4" 
                onClick={() => executePipelineMutation.mutate({ dataset_id: jobId, pipeline: insight.data.steps })}
                disabled={executePipelineMutation.isPending}
              >
                <Play className="w-4 h-4 mr-2" />
                Run Suggested Pipeline
              </Button>
            </div>
          )}

          {insight?.type === "transform" && (
            <div className="space-y-4 p-4 bg-zinc-50 dark:bg-zinc-900 rounded-lg border">
              <h3 className="font-bold text-lg text-emerald-700 dark:text-emerald-400">Transformation Successful</h3>
              <p className="text-sm text-zinc-700 dark:text-zinc-300">{insight.data.explanation}</p>
              
              <div className="bg-emerald-50 dark:bg-emerald-900/20 p-4 rounded-md border border-emerald-100 dark:border-emerald-900 mt-4">
                <h4 className="font-semibold text-emerald-800 dark:text-emerald-300 mb-2">Executed Pandas Code</h4>
                <pre className="text-xs text-emerald-700 dark:text-emerald-400 overflow-x-auto whitespace-pre-wrap">
                  {insight.data.python_code}
                </pre>
              </div>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}

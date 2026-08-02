"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Bot, Sparkles, Database, Play } from "lucide-react";
import { interactiveTransform } from "@/services/copilot";
import { useToast } from "@/components/ui/use-toast";

export function CopilotDataPrep({ jobId }: { jobId: string }) {
  const [intent, setIntent] = useState("");
  const [loading, setLoading] = useState(false);
  const [insight, setInsight] = useState<any>(null);
  const { toast } = useToast();

  const handleTransform = async () => {
    if (!intent) return;
    setLoading(true);
    try {
      const payload = {
        job_id: jobId,
        user_intent: intent
      };
      
      const data = await interactiveTransform(payload);
      setInsight(data);
      toast({ title: "Transformation Applied", description: "Dataset has been successfully modified." });
      
      if (data.success && data.download_url) {
        setTimeout(() => {
          const url = data.download_url.startsWith('http') ? data.download_url : `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${data.download_url}`;
          const a = document.createElement('a');
          a.href = url;
          a.download = 'processed_dataset.csv';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        }, 500);
      }
    } catch (err: any) {
      toast({ title: "Execution Failed", description: err.message, variant: "destructive" });
    } finally {
      setLoading(false);
      setIntent("");
    }
  };

  return (
    <Card className="w-full shadow-md border-indigo-100 dark:border-indigo-900/50">
      <CardHeader className="bg-indigo-50/50 dark:bg-indigo-950/20 pb-4">
        <CardTitle className="flex items-center gap-2 text-indigo-700 dark:text-indigo-400">
          <Bot className="w-5 h-5" />
          Interactive Data Prep
        </CardTitle>
        <CardDescription>
          Tell the Copilot how you want to clean or transform your dataset before running the pipeline.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6 pt-6">
        
        <div className="flex gap-2">
          <input 
            type="text"
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            placeholder="E.g., Impute missing values with median and drop outliers" 
            value={intent}
            onChange={(e) => setIntent(e.target.value)}
            disabled={loading}
          />
          <Button variant="default" onClick={handleTransform} disabled={loading || !intent} className="bg-indigo-600 hover:bg-indigo-700 text-white">
            {loading ? <Sparkles className="w-4 h-4 animate-pulse mr-2" /> : <Play className="w-4 h-4 mr-2" />}
            Apply
          </Button>
        </div>

        {insight && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="p-4 bg-emerald-50 dark:bg-emerald-950/30 rounded-lg border border-emerald-100 dark:border-emerald-900 flex justify-between items-center">
              <div>
                <h3 className="font-bold text-lg text-emerald-800 dark:text-emerald-400 mb-2">Transformation Successful</h3>
                <p className="text-sm text-emerald-700 dark:text-emerald-300">{insight.explanation}</p>
              </div>
              {insight.download_url && (
                <Button variant="outline" className="border-emerald-200 text-emerald-700 hover:bg-emerald-100 dark:border-emerald-800 dark:text-emerald-400 dark:hover:bg-emerald-900" onClick={() => {
                  const url = insight.download_url.startsWith('http') ? insight.download_url : `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${insight.download_url}`;
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = 'processed_dataset.csv';
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                }}>
                  Download Dataset
                </Button>
              )}
            </div>
            
            {insight.updated_stats && (
              <div className="border rounded-lg overflow-hidden">
                <div className="bg-zinc-50 dark:bg-zinc-900 px-4 py-2 border-b font-medium flex items-center gap-2 text-sm">
                  <Database className="w-4 h-4" /> Updated Dataset Statistics
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-zinc-50/50 dark:bg-zinc-900/50 text-zinc-500 dark:text-zinc-400">
                      <tr>
                        <th className="px-4 py-3 font-medium">Feature</th>
                        <th className="px-4 py-3 font-medium">Mean</th>
                        <th className="px-4 py-3 font-medium">Median</th>
                        <th className="px-4 py-3 font-medium">Std Dev</th>
                        <th className="px-4 py-3 font-medium">Nulls</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {Object.entries(insight.updated_stats).map(([feature, stats]: [string, any]) => (
                        <tr key={feature} className="hover:bg-zinc-50/50 dark:hover:bg-zinc-900/50">
                          <td className="px-4 py-3 font-medium">{feature}</td>
                          <td className="px-4 py-3">{stats.mean !== undefined ? stats.mean.toFixed(2) : '-'}</td>
                          <td className="px-4 py-3">{stats.median !== undefined ? stats.median.toFixed(2) : '-'}</td>
                          <td className="px-4 py-3">{stats.std !== undefined ? stats.std.toFixed(2) : '-'}</td>
                          <td className="px-4 py-3 text-amber-600 dark:text-amber-400 font-medium">{stats.nulls}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
            {insight.preview_data && insight.preview_data.length > 0 && (
              <div className="border rounded-lg overflow-hidden mt-4">
                <div className="bg-zinc-50 dark:bg-zinc-900 px-4 py-2 border-b font-medium flex items-center gap-2 text-sm">
                  <Database className="w-4 h-4" /> Data Preview (First {insight.preview_data.length} rows)
                </div>
                <div className="overflow-x-auto max-h-64">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-zinc-50/50 dark:bg-zinc-900/50 text-zinc-500 dark:text-zinc-400 sticky top-0">
                      <tr>
                        {Object.keys(insight.preview_data[0]).map((col) => (
                          <th key={col} className="px-4 py-3 font-medium whitespace-nowrap">{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {insight.preview_data.map((row: any, i: number) => (
                        <tr key={i} className="hover:bg-zinc-50/50 dark:hover:bg-zinc-900/50">
                          {Object.values(row).map((val: any, j: number) => (
                            <td key={j} className="px-4 py-2 whitespace-nowrap text-zinc-700 dark:text-zinc-300">
                              {val !== null && val !== undefined ? String(val) : '-'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
            
            <div className="bg-zinc-950 rounded-lg overflow-hidden border">
              <div className="bg-zinc-900 px-4 py-2 border-b border-zinc-800 text-xs font-mono text-zinc-400">Executed Python Code</div>
              <pre className="p-4 text-xs font-mono text-emerald-400 overflow-x-auto whitespace-pre-wrap">
                {insight.python_code}
              </pre>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

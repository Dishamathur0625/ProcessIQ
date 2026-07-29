"use client";

import { useQuery } from "@tanstack/react-query";
import { getJobStatus } from "@/services/job";
import { getReports, getVisualizations, getDownloadUrl } from "@/services/artifact";
import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { DownloadCloud, FileText, BarChart3, Database } from "lucide-react";
import dynamic from "next/dynamic";
import ReactMarkdown from "react-markdown";
import { CopilotDrawer } from "@/components/copilot/CopilotDrawer";
import { PredictionPlanner } from "@/components/planner/PredictionPlanner";
import { AutoMLDashboard } from "@/components/automl/AutoMLDashboard";

// Plotly needs to be dynamically imported to avoid SSR issues
const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export default function ResultsDashboard() {
  const { id } = useParams();
  const jobId = id as string;

  const { data: job } = useQuery({
    queryKey: ["jobStatus", jobId],
    queryFn: () => getJobStatus(jobId)
  });

  const { data: reports } = useQuery({
    queryKey: ["reports", jobId],
    queryFn: () => getReports(jobId),
    enabled: job?.status === "COMPLETED"
  });

  const { data: visualizations } = useQuery({
    queryKey: ["visualizations", jobId],
    queryFn: () => getVisualizations(jobId),
    enabled: job?.status === "COMPLETED"
  });

  if (job?.status !== "COMPLETED") {
      return (
          <div className="flex flex-col items-center justify-center pt-20 space-y-4">
              <h2 className="text-2xl font-bold">Job Not Ready</h2>
              <p className="text-zinc-500">The results for this job are not yet available.</p>
              <Button onClick={() => window.location.href=`/jobs/${jobId}/processing`}>View Timeline</Button>
          </div>
      );
  }

  const downloadUrl = getDownloadUrl(jobId);
  const vizData = visualizations?.content_json || visualizations;

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics Results</h1>
          <p className="text-zinc-500">Pipeline execution completed successfully.</p>
        </div>
        <div className="flex gap-2">
            <CopilotDrawer jobId={jobId} />
            <Button onClick={() => window.open(downloadUrl, "_blank")}>
                <DownloadCloud className="w-4 h-4 mr-2" /> Download Dataset
            </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-zinc-500">Status</CardTitle></CardHeader>
            <CardContent><p className="text-2xl font-bold text-green-600">Completed</p></CardContent>
        </Card>
        <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-zinc-500">Execution Time</CardTitle></CardHeader>
            <CardContent><p className="text-2xl font-bold">{((job.execution_time_ms || 0) / 1000).toFixed(2)}s</p></CardContent>
        </Card>
        <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-zinc-500">Pipeline Stages</CardTitle></CardHeader>
            <CardContent><p className="text-2xl font-bold">5 Executed</p></CardContent>
        </Card>
        <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-zinc-500">Artifacts</CardTitle></CardHeader>
            <CardContent><p className="text-2xl font-bold">Generated</p></CardContent>
        </Card>
      </div>

      <Tabs defaultValue="visualizations" className="w-full">
        <TabsList className="grid w-full grid-cols-5 mb-8">
          <TabsTrigger value="visualizations">Visualizations</TabsTrigger>
          <TabsTrigger value="reports">Reports & Quality</TabsTrigger>
          <TabsTrigger value="planner">Prediction Planner</TabsTrigger>
          <TabsTrigger value="automl">AutoML Execution</TabsTrigger>
          <TabsTrigger value="downloads">Download Center</TabsTrigger>
        </TabsList>
        
        <TabsContent value="visualizations" className="space-y-4">
            <Card>
                <CardHeader>
                    <CardTitle>Distribution Analysis</CardTitle>
                </CardHeader>
                <CardContent className="flex justify-center min-h-[400px]">
                    {vizData?.data ? (
                        <Plot
                            data={vizData.data}
                            layout={{
                                ...vizData.layout, 
                                width: undefined, // Let it be responsive if possible
                                autosize: true
                            }}
                            useResizeHandler={true}
                            style={{width: "100%", height: "100%"}}
                        />
                    ) : (
                        <p className="text-zinc-500 pt-10">No visualizations generated for this pipeline run.</p>
                    )}
                </CardContent>
            </Card>
        </TabsContent>

        <TabsContent value="reports" className="space-y-4">
            <Card>
                <CardHeader>
                    <CardTitle>Analytics Summary Report</CardTitle>
                </CardHeader>
                <CardContent className="prose dark:prose-invert max-w-none">
                    {reports?.content ? (
                        <ReactMarkdown>{reports.content}</ReactMarkdown>
                    ) : (
                        <p className="text-zinc-500">Report generation was skipped or unavailable.</p>
                    )}
                </CardContent>
            </Card>
        </TabsContent>

        <TabsContent value="planner" className="space-y-4">
            <PredictionPlanner jobId={jobId} />
        </TabsContent>

        <TabsContent value="automl" className="space-y-4">
            <AutoMLDashboard jobId={jobId} />
        </TabsContent>

        <TabsContent value="downloads" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                    <CardHeader className="flex flex-row items-center gap-4 space-y-0">
                        <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded"><Database className="text-blue-600 dark:text-blue-400 w-6 h-6" /></div>
                        <div>
                            <CardTitle>Cleaned Dataset</CardTitle>
                            <p className="text-sm text-zinc-500">processed_dataset.csv</p>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <Button variant="outline" className="w-full" onClick={() => window.open(downloadUrl, "_blank")}>Download Data</Button>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center gap-4 space-y-0">
                        <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded"><FileText className="text-purple-600 dark:text-purple-400 w-6 h-6" /></div>
                        <div>
                            <CardTitle>Pipeline Report</CardTitle>
                            <p className="text-sm text-zinc-500">Markdown Format</p>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <Button variant="outline" className="w-full">Download Report</Button>
                    </CardContent>
                </Card>
            </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

"use client";

import React from "react";
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

// Helper to parse basic inline markdown formatting (**bold**, *italic*, `code`) into styled JSX elements
function parseInlineStyles(text: string): React.ReactNode {
  if (!text) return "";
  
  const codeSplit = text.split("`");
  let key = 0;
  
  return (
    <>
      {codeSplit.map((codePart, codeIdx) => {
        const isCode = codeIdx % 2 === 1;
        if (isCode) {
          return (
            <code key={key++} className="px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-950 dark:text-zinc-50 font-mono text-xs border border-zinc-200/50 dark:border-zinc-700/50">
              {codePart}
            </code>
          );
        }
        
        const boldSplit = codePart.split("**");
        return (
          <React.Fragment key={key++}>
            {boldSplit.map((boldPart, boldIdx) => {
              const isBold = boldIdx % 2 === 1;
              if (isBold) {
                const italicSplit = boldPart.split("*");
                return (
                  <strong key={key++} className="font-extrabold text-zinc-950 dark:text-zinc-50">
                    {italicSplit.map((italicPart, italicIdx) => (
                      italicIdx % 2 === 1 ? <em key={key++} className="italic font-medium">{italicPart}</em> : italicPart
                    ))}
                  </strong>
                );
              }
              
              const italicSplit = boldPart.split("*");
              return (
                <React.Fragment key={key++}>
                  {italicSplit.map((italicPart, italicIdx) => (
                    italicIdx % 2 === 1 ? <em key={key++} className="italic text-zinc-500">{italicPart}</em> : italicPart
                  ))}
                </React.Fragment>
              );
            })}
          </React.Fragment>
        );
      })}
    </>
  );
}

// Custom Markdown Report parser to format quality improvement tables beautifully in Tailwind
function parseReport(content: string) {
  if (!content) return null;
  const lines = content.split('\n');
  const elements: React.ReactNode[] = [];
  let key = 0;
  
  let inTable = false;
  let tableHeaders: string[] = [];
  let tableRows: string[][] = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('|')) {
      if (line.includes('---|')) continue;
      const cells = line.split('|').map(c => c.trim()).filter((_, idx, arr) => idx > 0 && idx < arr.length - 1);
      if (!inTable) {
        inTable = true;
        tableHeaders = cells;
      } else {
        tableRows.push(cells);
      }
    } else {
      if (inTable && tableHeaders.length > 0) {
        elements.push(
          <div key={`table-${key++}`} className="overflow-x-auto my-6 border dark:border-zinc-800 rounded-xl bg-white dark:bg-zinc-950 shadow-sm">
            <table className="min-w-full divide-y divide-zinc-200 dark:divide-zinc-800">
              <thead className="bg-zinc-50/70 dark:bg-zinc-900/50">
                <tr>
                  {tableHeaders.map((h, idx) => (
                    <th key={idx} className="px-6 py-3.5 text-left text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {parseInlineStyles(h)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
                {tableRows.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-zinc-50 dark:hover:bg-zinc-900/50 transition-colors">
                    {row.map((cell, cIdx) => {
                      const cleanCell = cell.replace(/\*\*/g, '');
                      const isUp = cleanCell.includes('🟢');
                      const isDown = cleanCell.includes('🔴');
                      return (
                        <td key={cIdx} className={`px-6 py-4 whitespace-nowrap text-sm font-semibold ${isUp ? 'text-green-600 dark:text-green-400' : isDown ? 'text-red-600 dark:text-red-400' : 'text-zinc-800 dark:text-zinc-200'}`}>
                          {parseInlineStyles(cell)}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
        inTable = false;
        tableHeaders = [];
        tableRows = [];
      }
      if (line.startsWith('# ')) {
        elements.push(<h1 key={key++} className="text-3xl font-extrabold tracking-tight mt-8 mb-4 text-zinc-900 dark:text-zinc-100">{parseInlineStyles(line.substring(2))}</h1>);
      } else if (line.startsWith('## ')) {
        elements.push(<h2 key={key++} className="text-2xl font-bold tracking-tight mt-8 mb-3 text-zinc-900 dark:text-zinc-100 border-b pb-2 dark:border-zinc-800">{parseInlineStyles(line.substring(3))}</h2>);
      } else if (line.startsWith('### ')) {
        elements.push(<h3 key={key++} className="text-lg font-bold tracking-tight mt-6 mb-2 text-zinc-800 dark:text-zinc-200">{parseInlineStyles(line.substring(4))}</h3>);
      } else if (line.startsWith('- ') || line.startsWith('* ')) {
        elements.push(<li key={key++} className="list-disc ml-6 text-sm text-zinc-600 dark:text-zinc-400 my-1">{parseInlineStyles(line.substring(2))}</li>);
      } else if (line.match(/^\d+\.\s/)) {
        elements.push(<li key={key++} className="list-decimal ml-6 text-sm text-zinc-600 dark:text-zinc-400 my-1">{parseInlineStyles(line.replace(/^\d+\.\s/, ''))}</li>);
      } else if (line) {
        elements.push(<p key={key++} className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400 my-3">{parseInlineStyles(line)}</p>);
      }
    }
  }
  return <div className="space-y-3">{elements}</div>;
}

export default function ResultsDashboard() {
  const { id } = useParams();
  const jobId = id as string;
  const [activeTab, setActiveTab] = React.useState("visualizations");

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
  
  let plotObj: any = null;
  if (vizData) {
    let parsedData = vizData;
    if (typeof vizData === "string") {
      try {
        parsedData = JSON.parse(vizData);
      } catch (e) {
        console.error("Failed to parse visualizations JSON:", e);
      }
    }
    if (parsedData) {
      // Check for plotly_json nested structure
      let rawPlot = parsedData.plotly_json || parsedData;
      if (typeof rawPlot === "string") {
        try {
          rawPlot = JSON.parse(rawPlot);
        } catch (e) {
          console.error("Failed to parse plotly_json string:", e);
        }
      }
      
      if (rawPlot) {
        if (rawPlot.data) {
          plotObj = rawPlot;
        } else {
          const keys = Object.keys(rawPlot);
          if (keys.length > 0) {
            plotObj = rawPlot[keys[0]];
            if (typeof plotObj === "string") {
              try {
                plotObj = JSON.parse(plotObj);
              } catch (e) {}
            }
          }
        }
      }
    }
  }

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

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
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
                    {plotObj?.data ? (
                        <Plot
                            data={plotObj.data}
                            layout={{
                                ...plotObj.layout, 
                                width: undefined, // Let it be responsive if possible
                                autosize: true
                            }}
                            useResizeHandler={true}
                            style={{width: "100%", height: "400px"}}
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
                        parseReport(reports.content)
                    ) : (
                        <p className="text-zinc-500">Report generation was skipped or unavailable.</p>
                    )}
                </CardContent>
            </Card>
        </TabsContent>

        <TabsContent value="planner" className="space-y-4">
            <PredictionPlanner jobId={jobId} onProceed={() => setActiveTab("automl")} />
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

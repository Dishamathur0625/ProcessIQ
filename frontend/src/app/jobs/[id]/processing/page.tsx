"use client";

import { useQuery } from "@tanstack/react-query";
import { getJobStatus } from "@/services/job";
import { useParams, useRouter } from "next/navigation";
import { useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

const STAGES = [
  "QUEUED",
  "RUNNING", // includes validation, cleaning, feature engineering, selection
  "GENERATING_REPORTS",
  "GENERATING_VISUALIZATIONS",
  "COMPLETED"
];

export default function ProcessingPage() {
  const { id } = useParams();
  const router = useRouter();

  const { data: job } = useQuery({
    queryKey: ["jobStatus", id],
    queryFn: () => getJobStatus(id as string),
    refetchInterval: (query) => {
        const state = query.state?.data?.status;
        if (state === "COMPLETED") return false;
        if (state === "FAILED" || state === "CANCELLED") return false;
        if (state === "QUEUED") return 3000;
        if (state === "GENERATING_REPORTS") return 2000;
        return 1000; // RUNNING
    }
  });

  useEffect(() => {
    if (job?.status === "COMPLETED") {
        setTimeout(() => {
            router.push(`/jobs/${id}`);
        }, 1500); // short delay to show completion animation
    }
  }, [job?.status, id, router]);

  const currentStageIndex = STAGES.indexOf(job?.status || "QUEUED");

  return (
    <div className="max-w-3xl mx-auto space-y-6 pt-10">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Processing Dataset</h1>
        <p className="text-zinc-500">Executing deterministic Analytics Engine operations...</p>
      </div>

      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Pipeline Timeline</CardTitle>
        </CardHeader>
        <CardContent className="space-y-8 pl-8 pt-4">
          {STAGES.map((stage, index) => {
            const isCompleted = index < currentStageIndex;
            const isCurrent = index === currentStageIndex;
            const isPending = index > currentStageIndex;

            return (
              <motion.div 
                key={stage}
                initial={{ opacity: 0.5, x: -10 }}
                animate={{ 
                    opacity: isPending ? 0.3 : 1, 
                    x: 0,
                    scale: isCurrent ? 1.02 : 1 
                }}
                className="flex items-center gap-4 relative"
              >
                {/* Connecting line */}
                {index < STAGES.length - 1 && (
                    <div className={`absolute top-8 left-3 w-0.5 h-10 -ml-[1px] ${isCompleted ? 'bg-blue-600' : 'bg-zinc-200 dark:bg-zinc-800'}`} />
                )}

                <div className="relative z-10 flex items-center justify-center bg-white dark:bg-zinc-950">
                    {isCompleted ? (
                        <CheckCircle2 className="w-6 h-6 text-blue-600" />
                    ) : isCurrent ? (
                        <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
                    ) : (
                        <Circle className="w-6 h-6 text-zinc-300 dark:text-zinc-700" />
                    )}
                </div>

                <div>
                    <h3 className={`font-semibold ${isCurrent ? 'text-blue-600 dark:text-blue-400' : ''}`}>
                        {stage.replace(/_/g, " ")}
                    </h3>
                    {isCurrent && (
                        <p className="text-sm text-zinc-500">Currently executing stage...</p>
                    )}
                </div>
              </motion.div>
            );
          })}
        </CardContent>
      </Card>
    </div>
  );
}

"use client";

import Link from "next/link";
import { Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { getJobStatus } from "@/services/job";
import { useState, useEffect } from "react";

export function Navbar() {
  const pathname = usePathname();
  
  // Quick hack: we can poll localStorage for the latest active job id to show global status
  const [activeJobId, setActiveJobId] = useState<string | null>(null);

  useEffect(() => {
    // Basic polling to grab job ID from local storage if one was started
    const interval = setInterval(() => {
      const id = localStorage.getItem("active_job_id");
      setActiveJobId(id);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const { data: job } = useQuery({
    queryKey: ["jobStatus", activeJobId],
    queryFn: () => getJobStatus(activeJobId!),
    enabled: !!activeJobId,
    refetchInterval: (query) => {
        const state = query.state?.data?.status;
        if (state === "COMPLETED" || state === "FAILED" || state === "CANCELLED") {
            return false;
        }
        return 3000;
    }
  });

  return (
    <nav className="border-b bg-white dark:bg-zinc-950 sticky top-0 z-50">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-semibold text-lg">
          <div className="w-8 h-8 bg-black dark:bg-white text-white dark:text-black flex items-center justify-center rounded-md font-bold">
            IQ
          </div>
          <span className="hidden sm:inline-block">ProcessIQ</span>
        </Link>
        
        <div className="flex flex-1 items-center justify-center">
            {job && job.status !== "COMPLETED" && job.status !== "FAILED" && (
                <div className="hidden md:flex items-center gap-2 px-4 py-1.5 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded-full text-sm font-medium animate-pulse">
                    <Activity className="w-4 h-4" />
                    <span>Processing Job: {job.status}</span>
                </div>
            )}
        </div>

        <div className="flex items-center gap-4">
          <Link href="/dashboard">
            <Button variant={pathname === "/dashboard" ? "secondary" : "ghost"}>Dashboard</Button>
          </Link>
          <Link href="/upload">
            <Button>Upload Dataset</Button>
          </Link>
        </div>
      </div>
    </nav>
  );
}

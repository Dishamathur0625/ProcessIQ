"use client";

import { useQuery } from "@tanstack/react-query";
import { getHealth } from "@/services/health";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Server, Activity, Database, Zap } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    refetchInterval: 10000,
  });

  return (
    <div className="max-w-6xl mx-auto space-y-8 pt-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Dashboard</h1>
          <p className="text-zinc-500">Monitor Analytics Engine infrastructure and recent jobs.</p>
        </div>
        <Link href="/upload">
          <Button>New Dataset</Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-500">API Gateway</CardTitle>
            <Server className="w-4 h-4 text-zinc-500" />
          </CardHeader>
          <CardContent>
            <p className={`text-2xl font-bold ${health?.api === "healthy" ? 'text-green-600' : 'text-zinc-300'}`}>
              {health?.api === "healthy" ? "Online" : "Unknown"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-500">PostgreSQL</CardTitle>
            <Database className="w-4 h-4 text-zinc-500" />
          </CardHeader>
          <CardContent>
            <p className={`text-2xl font-bold ${health?.postgres === "healthy" ? 'text-green-600' : 'text-zinc-300'}`}>
              {health?.postgres === "healthy" ? "Connected" : "Unknown"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-500">Redis Broker</CardTitle>
            <Zap className="w-4 h-4 text-zinc-500" />
          </CardHeader>
          <CardContent>
            <p className={`text-2xl font-bold ${health?.redis === "healthy" ? 'text-green-600' : 'text-zinc-300'}`}>
              {health?.redis === "healthy" ? "Connected" : "Unknown"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-500">Celery Workers</CardTitle>
            <Activity className="w-4 h-4 text-zinc-500" />
          </CardHeader>
          <CardContent>
            <p className={`text-2xl font-bold ${health?.worker === "healthy" ? 'text-green-600' : 'text-zinc-300'}`}>
              {health?.worker === "healthy" ? "Active" : "Unknown"}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Pipeline Executions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-10 text-zinc-500">
            <p>No jobs found. (List endpoint not implemented in this demo).</p>
            <Link href="/upload">
                <Button variant="link" className="mt-2">Upload a dataset to start</Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

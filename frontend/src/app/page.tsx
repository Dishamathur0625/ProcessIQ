import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] text-center max-w-4xl mx-auto space-y-8">
      <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-zinc-900 dark:text-zinc-50">
        Enterprise-Grade <br />
        <span className="text-blue-600 dark:text-blue-500">Data Preprocessing</span>
      </h1>
      
      <p className="text-xl text-zinc-600 dark:text-zinc-400 max-w-2xl leading-relaxed">
        ProcessIQ is a deterministic, research-backed analytics engine designed to automatically profile, validate, clean, and engineer features from your raw datasets. Built for IEEE benchmarks and enterprise ML readiness.
      </p>
      
      <div className="flex flex-col sm:flex-row gap-4 pt-4">
        <Link href="/upload">
          <Button size="lg" className="h-12 px-8 text-lg font-medium">
            Start Processing Dataset
          </Button>
        </Link>
        <Link href="/dashboard">
          <Button size="lg" variant="outline" className="h-12 px-8 text-lg font-medium">
            View Dashboard
          </Button>
        </Link>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-16 text-left">
        <div className="space-y-3">
          <h3 className="text-lg font-semibold">Deterministic Execution</h3>
          <p className="text-zinc-500 dark:text-zinc-400">Cryptographic audit trails and strictly reproducible data transformations without non-deterministic side effects.</p>
        </div>
        <div className="space-y-3">
          <h3 className="text-lg font-semibold">IEEE Benchmarked</h3>
          <p className="text-zinc-500 dark:text-zinc-400">Evaluated against IEEE standard benchmarks covering diverse dataset typologies, scoring consistently high IDRS.</p>
        </div>
        <div className="space-y-3">
          <h3 className="text-lg font-semibold">End-to-End Orchestrated</h3>
          <p className="text-zinc-500 dark:text-zinc-400">From dataset fingerprinting to advanced feature selection, orchestrated asynchronously over Redis and Celery.</p>
        </div>
      </div>
    </div>
  );
}

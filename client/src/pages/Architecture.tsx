import { Layout } from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { GitBranch, Database, Box, Server, Activity, ShieldCheck, Layers } from "lucide-react";

export default function Architecture() {
  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-1">System Architecture</h1>
        <p className="text-muted-foreground">Overview of the MLOps pipeline and tech stack</p>
      </div>

      <div className="grid gap-8">
        {/* Diagram Area */}
        <div className="bg-card/50 border border-border rounded-xl p-8 relative overflow-hidden group">
          <div className="absolute inset-0 bg-grid-white/5 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))]" />
          
          <div className="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-8 text-center items-center">
             {/* Data Stage */}
             <div className="space-y-4">
               <div className="mx-auto w-16 h-16 bg-blue-500/20 rounded-2xl flex items-center justify-center border border-blue-500/50">
                 <Database className="w-8 h-8 text-blue-500" />
               </div>
               <div>
                 <h3 className="font-bold text-lg">Data Ingestion</h3>
                 <p className="text-sm text-muted-foreground">PostgreSQL + DVC</p>
               </div>
               <div className="h-px w-full bg-border" />
               <div className="text-xs text-muted-foreground font-mono">
                 Raw data validation via Great Expectations
               </div>
             </div>

             {/* Arrow */}
             <div className="hidden md:flex justify-center">
               <div className="w-full h-0.5 bg-gradient-to-r from-blue-500/50 to-purple-500/50" />
             </div>

             {/* Training Stage */}
             <div className="space-y-4">
               <div className="mx-auto w-16 h-16 bg-purple-500/20 rounded-2xl flex items-center justify-center border border-purple-500/50">
                 <Box className="w-8 h-8 text-purple-500" />
               </div>
               <div>
                 <h3 className="font-bold text-lg">Model Training</h3>
                 <p className="text-sm text-muted-foreground">XGBoost + MLflow</p>
               </div>
               <div className="h-px w-full bg-border" />
               <div className="text-xs text-muted-foreground font-mono">
                 Experiment tracking & registry
               </div>
             </div>

             {/* Arrow */}
             <div className="hidden md:flex justify-center">
               <div className="w-full h-0.5 bg-gradient-to-r from-purple-500/50 to-emerald-500/50" />
             </div>

             {/* Serving Stage */}
             <div className="space-y-4">
               <div className="mx-auto w-16 h-16 bg-emerald-500/20 rounded-2xl flex items-center justify-center border border-emerald-500/50">
                 <Server className="w-8 h-8 text-emerald-500" />
               </div>
               <div>
                 <h3 className="font-bold text-lg">Serving</h3>
                 <p className="text-sm text-muted-foreground">FastAPI + Docker</p>
               </div>
               <div className="h-px w-full bg-border" />
               <div className="text-xs text-muted-foreground font-mono">
                 Real-time inference endpoint
               </div>
             </div>
          </div>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="glass-panel">
            <CardHeader className="flex flex-row items-center gap-4">
              <div className="p-2 bg-primary/10 rounded-lg">
                <GitBranch className="w-6 h-6 text-primary" />
              </div>
              <div>
                <CardTitle>Version Control</CardTitle>
                <CardDescription>Code and Data</CardDescription>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                We strictly separate code versioning (Git) from data versioning (DVC). This ensures reproducibility of experiments by linking specific data commits to model versions.
              </p>
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary">DVC</Badge>
                <Badge variant="secondary">Git</Badge>
                <Badge variant="secondary">S3 Bucket</Badge>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-panel">
            <CardHeader className="flex flex-row items-center gap-4">
               <div className="p-2 bg-orange-500/10 rounded-lg">
                <ShieldCheck className="w-6 h-6 text-orange-500" />
              </div>
              <div>
                <CardTitle>Data Validation</CardTitle>
                <CardDescription>Quality Assurance</CardDescription>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Before any training run, data passes through Great Expectations suites. If data drift or schema violations are detected, the pipeline halts automatically.
              </p>
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary">Great Expectations</Badge>
                <Badge variant="secondary">PyTest</Badge>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-panel">
             <CardHeader className="flex flex-row items-center gap-4">
               <div className="p-2 bg-pink-500/10 rounded-lg">
                <Layers className="w-6 h-6 text-pink-500" />
              </div>
              <div>
                <CardTitle>Orchestration</CardTitle>
                <CardDescription>Workflow Management</CardDescription>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Apache Airflow manages the DAG (Directed Acyclic Graph) of tasks: Extraction → Validation → Transformation → Training → Evaluation → Deployment.
              </p>
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary">Airflow</Badge>
                <Badge variant="secondary">Celery Workers</Badge>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-panel">
             <CardHeader className="flex flex-row items-center gap-4">
               <div className="p-2 bg-cyan-500/10 rounded-lg">
                <Activity className="w-6 h-6 text-cyan-500" />
              </div>
              <div>
                <CardTitle>Monitoring</CardTitle>
                <CardDescription>Observability</CardDescription>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Prometheus scrapes metrics from the model endpoint. Grafana dashboards visualize request rates, latency, and prediction distribution to detect concept drift.
              </p>
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary">Prometheus</Badge>
                <Badge variant="secondary">Grafana</Badge>
                <Badge variant="secondary">Evidently AI</Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
}

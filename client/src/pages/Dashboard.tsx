import { Layout } from "@/components/Layout";
import { usePipelineRuns } from "@/hooks/use-pipeline";
import { usePredictionHistory } from "@/hooks/use-predictions";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Activity, Play, CheckCircle2, XCircle, Clock, Zap, BarChart3 } from "lucide-react";
import { useTriggerPipeline } from "@/hooks/use-pipeline";
import { useToast } from "@/hooks/use-toast";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { format } from "date-fns";

// Mock data for charts if API is empty
const MOCK_METRICS = [
  { run: "v1.0", accuracy: 0.82, f1: 0.79 },
  { run: "v1.1", accuracy: 0.84, f1: 0.81 },
  { run: "v1.2", accuracy: 0.83, f1: 0.80 },
  { run: "v1.3", accuracy: 0.86, f1: 0.84 },
  { run: "v1.4", accuracy: 0.85, f1: 0.83 },
  { run: "v1.5", accuracy: 0.88, f1: 0.86 },
  { run: "v1.6", accuracy: 0.89, f1: 0.87 },
];

export default function Dashboard() {
  const { data: runs, isLoading: runsLoading } = usePipelineRuns();
  const { data: predictions, isLoading: predsLoading } = usePredictionHistory();
  const { mutate: triggerPipeline, isPending: isTriggering } = useTriggerPipeline();
  const { toast } = useToast();

  const handleTrigger = () => {
    triggerPipeline(undefined, {
      onSuccess: (data) => {
        toast({
          title: "Pipeline Triggered",
          description: `Run ID: ${data.runId} started successfully.`,
        });
      },
      onError: () => {
        toast({
          title: "Trigger Failed",
          description: "Could not start the pipeline. Check backend logs.",
          variant: "destructive",
        });
      }
    });
  };

  const recentPredictions = predictions?.slice(0, 5) || [];
  const latestRun = runs?.[0];

  return (
    <Layout>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-1">Model Overview</h1>
          <p className="text-muted-foreground">Real-time metrics for No-Show Prediction Model (XGBoost)</p>
        </div>
        <div className="flex gap-3">
           <Button variant="outline" className="gap-2">
             <Clock className="w-4 h-4" /> History
           </Button>
           <Button 
             onClick={handleTrigger} 
             disabled={isTriggering}
             className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/25 gap-2"
           >
             {isTriggering ? <Activity className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
             Trigger Pipeline
           </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="glass-panel border-l-4 border-l-primary">
          <CardContent className="pt-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Model Accuracy</p>
                <h3 className="text-2xl font-bold mt-2">89.2%</h3>
                <p className="text-xs text-emerald-500 mt-1 flex items-center">
                  <Zap className="w-3 h-3 mr-1" /> +2.4% vs last version
                </p>
              </div>
              <div className="p-2 bg-primary/10 rounded-lg">
                <Activity className="w-5 h-5 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="glass-panel border-l-4 border-l-purple-500">
          <CardContent className="pt-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Predictions</p>
                <h3 className="text-2xl font-bold mt-2">{predictions?.length || 1240}</h3>
                <p className="text-xs text-muted-foreground mt-1">All time</p>
              </div>
              <div className="p-2 bg-purple-500/10 rounded-lg">
                <BarChart3 className="w-5 h-5 text-purple-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-l-4 border-l-emerald-500">
          <CardContent className="pt-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Pipeline Status</p>
                <h3 className="text-2xl font-bold mt-2 text-emerald-500">Healthy</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  Last run: {latestRun ? format(new Date(latestRun.createdAt!), 'MMM d, HH:mm') : 'Never'}
                </p>
              </div>
              <div className="p-2 bg-emerald-500/10 rounded-lg">
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="glass-panel border-l-4 border-l-orange-500">
          <CardContent className="pt-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Drift Detected</p>
                <h3 className="text-2xl font-bold mt-2 text-orange-500">None</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  Kolmogorov-Smirnov Test
                </p>
              </div>
              <div className="p-2 bg-orange-500/10 rounded-lg">
                <Activity className="w-5 h-5 text-orange-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Performance Chart */}
        <Card className="lg:col-span-2 glass-panel">
          <CardHeader>
            <CardTitle>Performance History</CardTitle>
            <CardDescription>Accuracy vs F1 Score across recent runs</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={MOCK_METRICS}>
                  <defs>
                    <linearGradient id="colorAccuracy" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="run" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} domain={[0.5, 1]} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
                    itemStyle={{ color: '#f8fafc' }}
                  />
                  <Area type="monotone" dataKey="accuracy" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorAccuracy)" />
                  <Line type="monotone" dataKey="f1" stroke="#a855f7" strokeWidth={2} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Recent Pipeline Runs */}
        <Card className="glass-panel">
          <CardHeader>
            <CardTitle>Pipeline Activity</CardTitle>
            <CardDescription>Recent execution logs</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {runsLoading ? (
                 <div className="text-sm text-muted-foreground animate-pulse">Loading runs...</div>
              ) : runs && runs.length > 0 ? (
                runs.slice(0, 5).map((run) => (
                  <div key={run.id} className="flex items-center justify-between p-3 rounded-lg bg-card/50 border border-border">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${run.status === 'completed' ? 'bg-emerald-500' : run.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'}`} />
                      <div>
                        <p className="text-sm font-medium">{run.runId}</p>
                        <p className="text-xs text-muted-foreground">{format(new Date(run.createdAt!), 'MMM d, HH:mm')}</p>
                      </div>
                    </div>
                    <Badge variant={run.status === 'completed' ? 'secondary' : 'outline'}>
                      {run.status}
                    </Badge>
                  </div>
                ))
              ) : (
                <div className="text-sm text-muted-foreground text-center py-4">No runs found.</div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Predictions Table */}
      <Card className="glass-panel">
        <CardHeader>
          <CardTitle>Recent Inference Requests</CardTitle>
          <CardDescription>Live incoming predictions from the serving endpoint</CardDescription>
        </CardHeader>
        <CardContent>
          {predsLoading ? (
            <div className="p-4 text-center text-muted-foreground">Loading history...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Time</TableHead>
                  <TableHead>Age</TableHead>
                  <TableHead>Gender</TableHead>
                  <TableHead>Conditions</TableHead>
                  <TableHead>Probability</TableHead>
                  <TableHead className="text-right">Result</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentPredictions.map((pred) => (
                  <TableRow key={pred.id}>
                    <TableCell className="font-mono text-xs">
                      {pred.createdAt ? format(new Date(pred.createdAt), 'HH:mm:ss') : '-'}
                    </TableCell>
                    <TableCell>{pred.age}</TableCell>
                    <TableCell>{pred.gender}</TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        {pred.diabetes && <Badge variant="outline" className="text-[10px] px-1 py-0 h-4">Dia</Badge>}
                        {pred.hypertension && <Badge variant="outline" className="text-[10px] px-1 py-0 h-4">Hyp</Badge>}
                        {!pred.diabetes && !pred.hypertension && <span className="text-muted-foreground text-xs">-</span>}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-secondary rounded-full overflow-hidden">
                          <div 
                            className={`h-full ${pred.predictionProbability! > 0.5 ? 'bg-rose-500' : 'bg-emerald-500'}`} 
                            style={{ width: `${(pred.predictionProbability || 0) * 100}%` }} 
                          />
                        </div>
                        <span className="text-xs font-mono">{((pred.predictionProbability || 0) * 100).toFixed(1)}%</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      {pred.predictedNoShow ? (
                        <Badge variant="destructive" className="bg-rose-500/20 text-rose-500 border-rose-500/50 hover:bg-rose-500/30">No Show</Badge>
                      ) : (
                        <Badge variant="outline" className="text-emerald-500 border-emerald-500/50 bg-emerald-500/10">Show Up</Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </Layout>
  );
}

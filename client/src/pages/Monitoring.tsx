import { useState, useEffect } from "react";
import { Layout } from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  RefreshCw,
  Database,
  Workflow,
  Activity,
  BarChart3,
  Eye,
  Server,
  Container,
  GitBranch
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface ComponentStatus {
  status: string;
  [key: string]: any;
}

interface MonitoringData {
  timestamp: string;
  components: {
    dvc: ComponentStatus;
    airflow: ComponentStatus;
    mlflow: ComponentStatus;
    evidently: ComponentStatus;
    prometheus: ComponentStatus;
    grafana: ComponentStatus;
    docker: ComponentStatus;
    github_actions: ComponentStatus;
  };
}

const ComponentCard = ({ 
  title, 
  icon: Icon, 
  data, 
  color 
}: { 
  title: string; 
  icon: any; 
  data: ComponentStatus; 
  color: string;
}) => {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "success":
        return <Badge className="bg-emerald-500"><CheckCircle2 className="w-3 h-3 mr-1" />Active</Badge>;
      case "configured":
        return <Badge className="bg-blue-500"><AlertCircle className="w-3 h-3 mr-1" />Configured</Badge>;
      case "error":
        return <Badge variant="destructive"><XCircle className="w-3 h-3 mr-1" />Error</Badge>;
      case "not_configured":
        return <Badge variant="secondary"><AlertCircle className="w-3 h-3 mr-1" />Not Configured</Badge>;
      case "not_installed":
        return <Badge variant="outline"><AlertCircle className="w-3 h-3 mr-1" />Not Installed</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const renderDetails = () => {
    const details: JSX.Element[] = [];
    
    Object.entries(data).forEach(([key, value]) => {
      if (key === "status" || key === "error" || key === "message") return;
      
      if (typeof value === "boolean") {
        details.push(
          <div key={key} className="flex justify-between items-center text-sm">
            <span className="text-muted-foreground capitalize">{key.replace(/_/g, " ")}:</span>
            <span className={value ? "text-emerald-500" : "text-gray-400"}>
              {value ? "✓" : "✗"}
            </span>
          </div>
        );
      } else if (typeof value === "number") {
        details.push(
          <div key={key} className="flex justify-between items-center text-sm">
            <span className="text-muted-foreground capitalize">{key.replace(/_/g, " ")}:</span>
            <span className="font-semibold">{value}</span>
          </div>
        );
      } else if (typeof value === "string" && value.length < 100) {
        details.push(
          <div key={key} className="flex justify-between items-center text-sm">
            <span className="text-muted-foreground capitalize">{key.replace(/_/g, " ")}:</span>
            <span className="font-mono text-xs">{value}</span>
          </div>
        );
      } else if (Array.isArray(value) && value.length > 0) {
        details.push(
          <div key={key} className="text-sm">
            <span className="text-muted-foreground capitalize">{key.replace(/_/g, " ")}:</span>
            <ul className="ml-4 mt-1 space-y-1">
              {value.slice(0, 5).map((item, idx) => (
                <li key={idx} className="text-xs">
                  • {typeof item === "object" ? item.name || item.title || JSON.stringify(item).slice(0, 50) : item}
                </li>
              ))}
              {value.length > 5 && <li className="text-xs text-muted-foreground">... and {value.length - 5} more</li>}
            </ul>
          </div>
        );
      }
    });
    
    return details.length > 0 ? details : <p className="text-sm text-muted-foreground">No additional details</p>;
  };

  return (
    <Card className="glass-panel">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`p-2 rounded-lg bg-${color}-500/10`}>
              <Icon className={`w-5 h-5 text-${color}-500`} />
            </div>
            <CardTitle className="text-lg">{title}</CardTitle>
          </div>
          {getStatusBadge(data.status)}
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {data.error && (
          <div className="p-2 bg-red-500/10 border border-red-500/20 rounded text-xs text-red-400">
            {data.error}
          </div>
        )}
        {data.message && !data.error && (
          <div className="p-2 bg-blue-500/10 border border-blue-500/20 rounded text-xs text-blue-400">
            {data.message}
          </div>
        )}
        {renderDetails()}
      </CardContent>
    </Card>
  );
};

export default function Monitoring() {
  const [data, setData] = useState<MonitoringData | null>(null);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  const fetchMonitoringData = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/monitoring/status");
      if (!response.ok) throw new Error("Failed to fetch monitoring data");
      const result = await response.json();
      setData(result);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch monitoring status",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const generateDriftReport = async () => {
    try {
      toast({
        title: "Generating Report",
        description: "Creating drift detection report...",
      });
      
      const response = await fetch("/api/monitoring/drift-report", {
        method: "POST",
      });
      
      if (!response.ok) throw new Error("Failed to generate report");
      
      const result = await response.json();
      
      toast({
        title: "Success",
        description: result.message || "Drift report generated successfully",
      });
      
      // Refresh monitoring data
      await fetchMonitoringData();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate drift report",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    fetchMonitoringData();
  }, []);

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-96">
          <RefreshCw className="w-8 h-8 animate-spin text-primary" />
        </div>
      </Layout>
    );
  }

  if (!data) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <p className="text-lg">Failed to load monitoring data</p>
            <Button onClick={fetchMonitoringData} className="mt-4">
              Retry
            </Button>
          </div>
        </div>
      </Layout>
    );
  }

  const componentConfig = [
    { key: "dvc", title: "DVC (Data Version Control)", icon: Database, color: "blue" },
    { key: "airflow", title: "Apache Airflow", icon: Workflow, color: "purple" },
    { key: "mlflow", title: "MLflow", icon: Activity, color: "emerald" },
    { key: "evidently", title: "Evidently AI", icon: Eye, color: "orange" },
    { key: "prometheus", title: "Prometheus", icon: BarChart3, color: "red" },
    { key: "grafana", title: "Grafana", icon: Server, color: "yellow" },
    { key: "docker", title: "Docker", icon: Container, color: "cyan" },
    { key: "github_actions", title: "GitHub Actions", icon: GitBranch, color: "green" },
  ];

  const successCount = Object.values(data.components).filter(c => c.status === "success").length;
  const errorCount = Object.values(data.components).filter(c => c.status === "error").length;
  const healthPercentage = Math.round((successCount / Object.keys(data.components).length) * 100);

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-1">System Monitoring</h1>
            <p className="text-muted-foreground">Real-time status of all MLOps components</p>
          </div>
          <div className="flex gap-3">
            <Button 
              variant="outline" 
              onClick={generateDriftReport}
              className="gap-2"
            >
              <Eye className="w-4 h-4" />
              Generate Drift Report
            </Button>
            <Button 
              onClick={fetchMonitoringData}
              className="gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh Status
            </Button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="glass-panel border-l-4 border-l-emerald-500">
            <CardContent className="pt-6">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">System Health</p>
                  <h3 className="text-3xl font-bold mt-2">{healthPercentage}%</h3>
                  <p className="text-xs text-muted-foreground mt-1">{successCount} of {Object.keys(data.components).length} active</p>
                </div>
                <div className="p-2 bg-emerald-500/10 rounded-lg">
                  <Activity className="w-6 h-6 text-emerald-500" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-panel border-l-4 border-l-blue-500">
            <CardContent className="pt-6">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Components</p>
                  <h3 className="text-3xl font-bold mt-2">{Object.keys(data.components).length}</h3>
                  <p className="text-xs text-muted-foreground mt-1">Total configured</p>
                </div>
                <div className="p-2 bg-blue-500/10 rounded-lg">
                  <Server className="w-6 h-6 text-blue-500" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-panel border-l-4 border-l-orange-500">
            <CardContent className="pt-6">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Last Updated</p>
                  <h3 className="text-lg font-bold mt-2">
                    {new Date(data.timestamp).toLocaleTimeString()}
                  </h3>
                  <p className="text-xs text-muted-foreground mt-1">
                    {errorCount > 0 ? `${errorCount} errors detected` : "All systems operational"}
                  </p>
                </div>
                <div className="p-2 bg-orange-500/10 rounded-lg">
                  <RefreshCw className="w-6 h-6 text-orange-500" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Component Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {componentConfig.map(({ key, title, icon, color }) => (
            <ComponentCard
              key={key}
              title={title}
              icon={icon}
              data={data.components[key as keyof typeof data.components]}
              color={color}
            />
          ))}
        </div>
      </div>
    </Layout>
  );
}

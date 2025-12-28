import { Link, useLocation } from "wouter";
import { LayoutDashboard, BrainCircuit, Network, Github, Settings, Activity, Eye } from "lucide-react";

export function Layout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();

  const navItems = [
    { href: "/", label: "Dashboard", icon: LayoutDashboard },
    { href: "/predict", label: "Predictor", icon: BrainCircuit },
    { href: "/architecture", label: "Architecture", icon: Network },
    { href: "/monitoring", label: "Monitoring", icon: Eye },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground flex">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-card/30 hidden md:flex flex-col fixed h-full z-10">
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center border border-primary/30">
              <Activity className="w-5 h-5 text-primary" />
            </div>
            <h1 className="font-bold text-lg tracking-tight">MLOps Control</h1>
          </div>
          <div className="mt-2 text-xs text-muted-foreground font-mono px-1">
            v2.4.0-stable
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location === item.href;
            return (
              <Link key={item.href} href={item.href}>
                <div className={`sidebar-link cursor-pointer ${isActive ? 'active' : ''}`}>
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                  {isActive && (
                    <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
                  )}
                </div>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-border">
          <div className="bg-card border border-border rounded-lg p-3">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-medium text-muted-foreground">System Operational</span>
            </div>
            <div className="text-[10px] text-muted-foreground font-mono">
              Cluster: us-east-1a<br />
              Latency: 24ms
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 md:ml-64 min-h-screen relative overflow-hidden">
        {/* Ambient background glow */}
        <div className="absolute top-0 left-0 w-full h-96 bg-primary/5 rounded-full blur-[100px] pointer-events-none -translate-y-1/2" />
        
        <div className="relative z-10 p-6 md:p-10 max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}

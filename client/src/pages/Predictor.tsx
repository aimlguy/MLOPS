import { Layout } from "@/components/Layout";
import { usePredict } from "@/hooks/use-predictions";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { insertPredictionSchema, type PredictionInput } from "@shared/schema";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { BrainCircuit, Loader2, AlertCircle, CheckCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";
import { z } from "zod";

// We need to handle date strings from the form input, but the schema expects Date objects
const formSchema = insertPredictionSchema.extend({
  appointmentDay: z.string(),
  scheduledDay: z.string(),
});

export default function Predictor() {
  const { mutate: predict, isPending, error } = usePredict();
  const { toast } = useToast();
  const [result, setResult] = useState<{ probability: number; isNoShow: boolean } | null>(null);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      gender: "F",
      age: 30,
      neighbourhood: "Downtown",
      scholarship: false,
      hypertension: false,
      diabetes: false,
      alcoholism: false,
      handicap: 0,
      smsReceived: false,
      appointmentDay: new Date().toISOString().split('T')[0],
      scheduledDay: new Date().toISOString().split('T')[0],
    },
  });

  const onSubmit = (data: z.infer<typeof formSchema>) => {
    // Convert strings back to Dates for API
    const apiData: PredictionInput = {
      ...data,
      appointmentDay: new Date(data.appointmentDay),
      scheduledDay: new Date(data.scheduledDay),
    };

    predict(apiData, {
      onSuccess: (res) => {
        setResult(res);
        toast({
          title: "Prediction Complete",
          description: `Probability calculated: ${(res.probability * 100).toFixed(1)}%`,
        });
      },
      onError: (err) => {
        toast({
          title: "Error",
          description: err.message,
          variant: "destructive",
        });
      },
    });
  };

  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-1">Inference Engine</h1>
        <p className="text-muted-foreground">Manual entry interface for patient no-show prediction</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Input Form */}
        <div className="lg:col-span-2">
          <Card className="glass-panel">
            <CardHeader>
              <CardTitle>Patient Parameters</CardTitle>
              <CardDescription>Enter clinical and demographic data</CardDescription>
            </CardHeader>
            <CardContent>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Demographics */}
                    <FormField
                      control={form.control}
                      name="age"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Age</FormLabel>
                          <FormControl>
                            <Input 
                              type="number" 
                              {...field} 
                              onChange={e => field.onChange(Number(e.target.value))} 
                              className="bg-background/50"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="gender"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Gender</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger className="bg-background/50">
                                <SelectValue placeholder="Select gender" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="M">Male</SelectItem>
                              <SelectItem value="F">Female</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="neighbourhood"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Neighbourhood</FormLabel>
                          <FormControl>
                            <Input {...field} className="bg-background/50" />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="handicap"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Handicap Level (0-4)</FormLabel>
                          <FormControl>
                            <Input 
                              type="number" 
                              min="0" 
                              max="4" 
                              {...field} 
                              onChange={e => field.onChange(Number(e.target.value))}
                              className="bg-background/50"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {/* Dates */}
                    <FormField
                      control={form.control}
                      name="scheduledDay"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Scheduled Date</FormLabel>
                          <FormControl>
                            <Input type="date" {...field} className="bg-background/50" />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="appointmentDay"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Appointment Date</FormLabel>
                          <FormControl>
                            <Input type="date" {...field} className="bg-background/50" />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="space-y-4 pt-4 border-t border-border">
                    <h4 className="text-sm font-medium text-muted-foreground">Conditions & Status</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      <FormField
                        control={form.control}
                        name="diabetes"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-center justify-between rounded-lg border border-border p-3 bg-card/30">
                            <div className="space-y-0.5">
                              <FormLabel className="text-sm">Diabetes</FormLabel>
                            </div>
                            <FormControl>
                              <Switch
                                checked={field.value}
                                onCheckedChange={field.onChange}
                              />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="hypertension"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-center justify-between rounded-lg border border-border p-3 bg-card/30">
                            <div className="space-y-0.5">
                              <FormLabel className="text-sm">Hypertension</FormLabel>
                            </div>
                            <FormControl>
                              <Switch
                                checked={field.value}
                                onCheckedChange={field.onChange}
                              />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="alcoholism"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-center justify-between rounded-lg border border-border p-3 bg-card/30">
                            <div className="space-y-0.5">
                              <FormLabel className="text-sm">Alcoholism</FormLabel>
                            </div>
                            <FormControl>
                              <Switch
                                checked={field.value}
                                onCheckedChange={field.onChange}
                              />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                       <FormField
                        control={form.control}
                        name="scholarship"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-center justify-between rounded-lg border border-border p-3 bg-card/30">
                            <div className="space-y-0.5">
                              <FormLabel className="text-sm">Scholarship</FormLabel>
                            </div>
                            <FormControl>
                              <Switch
                                checked={field.value}
                                onCheckedChange={field.onChange}
                              />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                       <FormField
                        control={form.control}
                        name="smsReceived"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-center justify-between rounded-lg border border-border p-3 bg-card/30">
                            <div className="space-y-0.5">
                              <FormLabel className="text-sm">SMS Sent</FormLabel>
                            </div>
                            <FormControl>
                              <Switch
                                checked={field.value}
                                onCheckedChange={field.onChange}
                              />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                    </div>
                  </div>

                  <div className="pt-4">
                    <Button 
                      type="submit" 
                      className="w-full bg-primary hover:bg-primary/90 shadow-lg shadow-primary/25 h-12 text-lg font-semibold"
                      disabled={isPending}
                    >
                      {isPending ? (
                        <>
                          <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          <BrainCircuit className="mr-2 h-5 w-5" />
                          Run Prediction Model
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </Form>
            </CardContent>
          </Card>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-1">
          <Card className="h-full glass-panel flex flex-col">
            <CardHeader>
              <CardTitle>Analysis Result</CardTitle>
              <CardDescription>Model confidence output</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col justify-center items-center text-center p-8">
              {result ? (
                <div className="space-y-6 animate-in zoom-in-95 duration-300">
                  <div className={`relative w-40 h-40 rounded-full flex items-center justify-center border-8 ${result.isNoShow ? 'border-rose-500 bg-rose-500/10' : 'border-emerald-500 bg-emerald-500/10'}`}>
                     <span className={`text-4xl font-bold ${result.isNoShow ? 'text-rose-500' : 'text-emerald-500'}`}>
                       {(result.probability * 100).toFixed(0)}%
                     </span>
                     <div className="absolute bottom-2 text-xs font-medium text-muted-foreground uppercase tracking-widest">Risk</div>
                  </div>

                  <div>
                    <h3 className={`text-2xl font-bold mb-2 ${result.isNoShow ? 'text-rose-500' : 'text-emerald-500'}`}>
                      {result.isNoShow ? 'High Risk of No-Show' : 'Likely to Show Up'}
                    </h3>
                    <p className="text-muted-foreground text-sm">
                      Based on current model parameters (v1.6), this appointment has a {result.isNoShow ? 'high' : 'low'} probability of being missed.
                    </p>
                  </div>

                  <div className="w-full bg-secondary/50 p-4 rounded-lg text-left text-sm space-y-2 font-mono">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Model:</span>
                      <span>XGBoost Classifier</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Latency:</span>
                      <span>42ms</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Threshold:</span>
                      <span>0.50</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-muted-foreground space-y-4">
                  <div className="w-32 h-32 rounded-full bg-secondary/30 mx-auto flex items-center justify-center border-4 border-dashed border-muted">
                    <BrainCircuit className="w-12 h-12 opacity-50" />
                  </div>
                  <p>Enter patient details and submit to generate a prediction.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
}

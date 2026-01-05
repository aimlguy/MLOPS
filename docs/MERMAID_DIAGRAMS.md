# MLOps Project - Mermaid Workflow Diagrams

## 1. Overall System Architecture

```mermaid
graph TB
    subgraph "Data Layer"
        A[Raw CSV Data<br/>noshow.csv] -->|DVC Track| B[Data Version Control]
        B -->|Version Hash| C[Git Repository]
    end
    
    subgraph "Feature Engineering"
        A -->|Read| D[feature_engineering.py]
        D -->|Process| E[Processed Features]
        E -->|Save| F[features.csv]
    end
    
    subgraph "Training Pipeline"
        F -->|Input| G[train_baseline.py]
        F -->|Input| H[train_improved.py]
        F -->|Input| I[train_best.py]
        G -->|XGBoost| J[Baseline Model]
        H -->|Optimized| K[Improved Model]
        I -->|Hypertuned| L[Best Model]
        J --> M[Model Registry]
        K --> M
        L --> M
    end
    
    subgraph "Evaluation & Selection"
        M -->|Compare| N[evaluate.py]
        N -->|Metrics| O[Best Model Selection]
        O -->|Deploy| P[Production Model]
    end
    
    subgraph "Serving Layer"
        P -->|Load| Q[Express API<br/>Port 5000]
        Q -->|Endpoint| R[/api/predict]
        R -->|Response| S[Client Application<br/>React UI]
    end
    
    subgraph "Monitoring Stack"
        Q -->|Metrics| T[Prometheus<br/>Port 9090]
        T -->|Scrape| U[/api/metrics]
        T -->|Data| V[Grafana<br/>Port 3000]
        V -->|Visualize| W[Dashboards]
        Q -->|Drift Data| X[Evidently AI]
        X -->|Report| Y[drift_report.html]
    end
    
    subgraph "CI/CD"
        C -->|Push| Z[GitHub Actions]
        Z -->|Trigger| AA[Workflows]
        AA -->|Build| AB[Docker Image]
        AB -->|Deploy| AC[GCP Cloud Run]
    end

    style A fill:#e1f5ff
    style P fill:#c8e6c9
    style Q fill:#fff9c4
    style V fill:#ffccbc
```

## 2. CI/CD Pipeline (GitHub Actions)

```mermaid
graph LR
    subgraph "Triggers"
        A[Git Push to main] -->|or| B[Manual Dispatch]
        C[Pull Request] -->|or| D[Scheduled Cron]
    end
    
    A --> E{CI Workflow}
    B --> E
    C --> E
    D --> E
    
    E -->|1| F[Checkout Code]
    F -->|2| G[Setup Python 3.11]
    G -->|3| H[Install Dependencies]
    H -->|4| I[Run Linting]
    I -->|5| J[Type Checking]
    
    J -->|Pass| K{Model Training Workflow}
    K -->|1| L[Setup Environment]
    L -->|2| M[Train Baseline Model]
    M -->|3| N[Train Improved Model]
    N -->|4| O[Train Best Model]
    O -->|5| P[Evaluate Models]
    P -->|6| Q[Upload Artifacts]
    
    Q -->|Artifacts Ready| R{Deployment Workflow}
    R -->|1| S[Build Docker Image]
    S -->|2| T[Tag with version]
    T -->|3| U[Push to GCR]
    U -->|4| V[Deploy to Cloud Run]
    V -->|5| W[Health Check]
    W -->|Pass| X[Deployment Success]
    W -->|Fail| Y[Rollback]
    
    J -->|Fail| Z[Notify Failure]
    P -->|Fail| Z
    
    style X fill:#c8e6c9
    style Y fill:#ffcdd2
    style Z fill:#ffcdd2
```

## 3. DVC Training Pipeline

```mermaid
graph TD
    Start([DVC Repro Start]) -->|Stage 1| A[data_validation]
    
    A -->|Execute| B[feature_engineering.py]
    B -->|Deps Check| C{Dependencies Changed?}
    C -->|No| D[Use Cached Output]
    C -->|Yes| E[Process Raw Data]
    E -->|Transform| F[Create Features]
    F -->|Save| G[features.csv]
    G -->|Log| H[data_stats.json]
    
    H -->|Stage 2| I[train_baseline]
    I -->|Execute| J[train_baseline.py]
    J -->|Algorithm| K[XGBoost Default]
    K -->|Train| L[Baseline Model v1]
    L -->|Metrics| M[baseline_metrics.json]
    
    H -->|Stage 3| N[train_improved]
    N -->|Execute| O[train_improved.py]
    O -->|Algorithm| P[XGBoost Optimized]
    P -->|Train| Q[Improved Model v2]
    Q -->|Metrics| R[improved_metrics.json]
    
    H -->|Stage 4| S[train_best]
    S -->|Execute| T[train_best.py]
    T -->|Algorithm| U[XGBoost Hypertuned]
    U -->|Train| V[Best Model v3]
    V -->|Metrics| W[best_metrics.json]
    
    M --> X[Stage 5: evaluate]
    R --> X
    W --> X
    X -->|Compare| Y{Select Champion}
    Y -->|Accuracy| Z[Champion Model]
    Z -->|Register| AA[(Model Registry)]
    AA -->|Version| AB[models/champion.pkl]
    
    AB --> End([Pipeline Complete])
    D --> H
    
    style Z fill:#c8e6c9
    style AB fill:#fff9c4
```

## 4. Prediction/Inference Flow

```mermaid
sequenceDiagram
    autonumber
    participant User as User/Client
    participant UI as React UI<br/>(Port 5000)
    participant API as Express API<br/>/api/predict
    participant Model as Model Loader<br/>predict.py
    participant File as champion.pkl
    participant Prom as Prometheus<br/>Metrics
    
    User->>UI: Fill Patient Form
    UI->>UI: Validate Input Fields
    UI->>API: POST /api/predict<br/>{patient_data}
    
    API->>API: Log Request Start Time
    API->>Prom: Increment active_predictions
    
    API->>Model: predict(patient_data)
    Model->>File: Load Cached Model
    File-->>Model: Return Model Object
    
    Model->>Model: Preprocess Features
    Model->>Model: Run Inference
    Model->>Model: Get Prediction Probability
    
    Model-->>API: {is_no_show, probability}
    
    API->>API: Calculate Duration
    API->>Prom: Record prediction_latency
    API->>Prom: Increment predictions_total
    API->>Prom: Decrement active_predictions
    
    API-->>UI: JSON Response<br/>{prediction, confidence}
    UI->>UI: Display Result Card
    UI-->>User: Show Prediction Result
    
    Note over Prom: Metrics Available:<br/>- model_predictions_total<br/>- model_prediction_latency_seconds<br/>- model_active_predictions
```

## 5. Monitoring & Drift Detection

```mermaid
graph TB
    subgraph "Data Collection"
        A[Express API<br/>Port 5000] -->|Expose| B[/api/metrics Endpoint]
        A -->|Store| C[(Prediction History)]
    end
    
    subgraph "Metrics Scraping"
        B -->|HTTP GET| D[Prometheus Scraper<br/>Every 30s]
        D -->|Store| E[(Time Series DB)]
    end
    
    subgraph "Metrics Types"
        E -->|Counter| F[model_predictions_total]
        E -->|Histogram| G[model_prediction_latency]
        E -->|Gauge| H[model_active_predictions]
    end
    
    F --> I[Grafana Queries]
    G --> I
    H --> I
    
    subgraph "Visualization"
        I -->|Dashboard| J[Grafana UI<br/>Port 3000]
        J -->|Panel 1| K[Total Predictions]
        J -->|Panel 2| L[Active Predictions]
        J -->|Refresh 30s| J
    end
    
    subgraph "Drift Detection"
        C -->|Trigger| M[Generate Drift Report<br/>POST /api/monitoring/drift-report]
        M -->|Execute| N[monitoring.py]
        N -->|Load| O[Reference Dataset]
        N -->|Load| P[Current Predictions]
        O --> Q[Evidently AI]
        P --> Q
        Q -->|Analyze| R{Statistical Tests}
        R -->|KS Test| S[Feature Drift Score]
        R -->|Chi-Square| T[Categorical Drift]
        R -->|PSI| U[Population Stability]
        S --> V[Generate HTML Report]
        T --> V
        U --> V
        V -->|Save| W[reports/drift_report.html]
    end
    
    subgraph "Alerting"
        E -->|Query| X[Alert Rules<br/>alert_rules.yml]
        X -->|Condition| Y{High Drift?}
        Y -->|Yes| Z[Send Alert]
        Y -->|No| AA[Continue Monitoring]
    end
    
    style W fill:#fff9c4
    style J fill:#ffccbc
    style Z fill:#ffcdd2
```

## 6. Model Training Workflow Detail

```mermaid
stateDiagram-v2
    [*] --> DataIngestion
    
    DataIngestion --> FeatureEngineering: Raw CSV Available
    
    state FeatureEngineering {
        [*] --> LoadData
        LoadData --> ParseDates
        ParseDates --> CreateTimeFeatures
        CreateTimeFeatures --> EncodeCategories
        EncodeCategories --> ScaleNumerical
        ScaleNumerical --> [*]
    }
    
    FeatureEngineering --> DataValidation: Features Ready
    
    state DataValidation {
        [*] --> CheckSchema
        CheckSchema --> ValidateTypes
        ValidateTypes --> CheckMissing
        CheckMissing --> StatisticalChecks
        StatisticalChecks --> [*]
    }
    
    DataValidation --> ModelTraining: Validation Passed
    DataValidation --> [*]: Validation Failed
    
    state ModelTraining {
        [*] --> TrainBaseline
        TrainBaseline --> TrainImproved
        TrainImproved --> TrainBest
        
        state TrainBaseline {
            [*] --> XGBoostDefault
            XGBoostDefault --> CrossValidation
            CrossValidation --> SaveBaseline
            SaveBaseline --> [*]
        }
        
        state TrainImproved {
            [*] --> XGBoostOptimized
            XGBoostOptimized --> GridSearch
            GridSearch --> SaveImproved
            SaveImproved --> [*]
        }
        
        state TrainBest {
            [*] --> XGBoostHypertuned
            XGBoostHypertuned --> BayesianOpt
            BayesianOpt --> SaveBest
            SaveBest --> [*]
        }
        
        TrainBest --> [*]
    }
    
    ModelTraining --> Evaluation: 3 Models Trained
    
    state Evaluation {
        [*] --> LoadModels
        LoadModels --> ComputeMetrics
        ComputeMetrics --> CompareAccuracy
        CompareAccuracy --> SelectChampion
        SelectChampion --> [*]
    }
    
    Evaluation --> ModelRegistry: Champion Selected
    
    state ModelRegistry {
        [*] --> SaveChampion
        SaveChampion --> UpdateMetadata
        UpdateMetadata --> VersionTag
        VersionTag --> [*]
    }
    
    ModelRegistry --> Deployment
    Deployment --> [*]
```

## 7. Data Versioning with DVC

```mermaid
graph LR
    subgraph "Local Development"
        A[Modify noshow.csv] -->|Stage| B[dvc add data/raw/noshow.csv]
        B -->|Generate| C[noshow.csv.dvc]
        C -->|Contains| D[MD5 Hash + Metadata]
        D -->|Track| E[git add noshow.csv.dvc]
        E -->|Commit| F[git commit -m 'Update data']
    end
    
    subgraph "Remote Storage"
        F -->|Push Data| G[dvc push]
        G -->|Upload| H[(DVC Remote Cache)]
        H -->|Store| I[Original File by Hash]
    end
    
    subgraph "Team Collaboration"
        J[Teammate] -->|Clone| K[git clone repo]
        K -->|Contains| L[noshow.csv.dvc]
        L -->|Pull Data| M[dvc pull]
        M -->|Download| H
        H -->|Restore| N[noshow.csv]
    end
    
    subgraph "Pipeline Execution"
        N -->|Input| O[dvc repro]
        O -->|Check| P{Hash Changed?}
        P -->|No| Q[Use Cache]
        P -->|Yes| R[Rerun Stage]
        R -->|Output| S[New Artifacts]
        S -->|Track| T[dvc add]
        Q --> U[Pipeline Complete]
        T --> U
    end
    
    style H fill:#e1f5ff
    style U fill:#c8e6c9
```

## 8. API Request Flow

```mermaid
flowchart TD
    Start([HTTP Request]) -->|Method| A{Request Type?}
    
    A -->|POST /api/predict| B[Prediction Handler]
    A -->|GET /api/monitoring/status| C[Status Handler]
    A -->|POST /api/monitoring/drift-report| D[Drift Handler]
    A -->|GET /api/metrics| E[Metrics Handler]
    
    B -->|Parse| B1[Extract Patient Data]
    B1 -->|Validate| B2{Valid Input?}
    B2 -->|No| B3[Return 400 Error]
    B2 -->|Yes| B4[Call Model Inference]
    B4 -->|Predict| B5[Get Result]
    B5 -->|Log Metrics| B6[Update Prometheus]
    B6 -->|Response| B7[Return JSON]
    
    C -->|Check| C1[DVC Status]
    C1 -->|Check| C2[Evidently Status]
    C2 -->|Check| C3[Prometheus Status]
    C3 -->|Check| C4[Grafana Status]
    C4 -->|Check| C5[Docker Status]
    C5 -->|Check| C6[GitHub Actions Status]
    C6 -->|Aggregate| C7[Return Status JSON]
    
    D -->|Execute| D1[monitoring.py]
    D1 -->|Load Data| D2[Reference + Current]
    D2 -->|Analyze| D3[Evidently Report]
    D3 -->|Generate| D4[HTML Report]
    D4 -->|Save| D5[reports/drift_report.html]
    D5 -->|Response| D6[Return Success]
    
    E -->|Collect| E1[prom-client.register]
    E1 -->|Format| E2[Prometheus Metrics Format]
    E2 -->|Response| E3[Return Metrics Text]
    
    B3 --> End([HTTP Response])
    B7 --> End
    C7 --> End
    D6 --> End
    E3 --> End
    
    style B7 fill:#c8e6c9
    style C7 fill:#c8e6c9
    style D6 fill:#c8e6c9
    style E3 fill:#c8e6c9
    style B3 fill:#ffcdd2
```

## 9. Frontend Component Architecture

```mermaid
graph TD
    subgraph "React Application"
        A[App.tsx<br/>Main Entry] -->|Route /| B[Dashboard.tsx]
        A -->|Route /predictor| C[Predictor.tsx]
        A -->|Route /monitoring| D[Monitoring.tsx]
        A -->|Route /architecture| E[Architecture.tsx]
    end
    
    subgraph "Dashboard Page"
        B -->|Use Hook| F[usePipeline]
        F -->|Fetch| G[GET /api/pipeline/status]
        G -->|Data| H[Display Metrics Cards]
        H --> I[Recent Runs Table]
        H --> J[Model Comparison Chart]
    end
    
    subgraph "Predictor Page"
        C -->|Use Hook| K[usePredictions]
        C -->|Form| L[Patient Input Form]
        L -->|Submit| M[POST /api/predict]
        M -->|Response| N[Prediction Result Card]
        N -->|Display| O[Confidence Score]
        N -->|Display| P[Risk Assessment]
    end
    
    subgraph "Monitoring Page"
        D -->|Fetch| Q[GET /api/monitoring/status]
        Q -->|Data| R[Component Status Cards]
        R --> S[DVC Card]
        R --> T[Evidently Card]
        R --> U[Prometheus Card]
        R --> V[Grafana Card]
        R --> W[Docker Card]
        R --> X[GitHub Actions Card]
        D -->|Button| Y[Generate Drift Report]
        Y -->|POST| Z[/api/monitoring/drift-report]
    end
    
    subgraph "Architecture Page"
        E --> AA[System Diagram]
        E --> AB[Tech Stack Cards]
        E --> AC[Component Details]
    end
    
    subgraph "Shared Components"
        AD[Layout.tsx<br/>Navigation] --> A
        AE[UI Components<br/>shadcn/ui] --> B
        AE --> C
        AE --> D
        AE --> E
    end
    
    style N fill:#c8e6c9
    style H fill:#fff9c4
    style R fill:#ffccbc
```

## Usage Instructions

To use these diagrams:

1. **GitHub/GitLab**: Most support Mermaid natively in markdown files
2. **VS Code**: Install "Markdown Preview Mermaid Support" extension
3. **Mermaid Live Editor**: https://mermaid.live/
4. **Documentation**: Copy into README.md or docs

Each diagram represents a different aspect of the MLOps pipeline workflow.

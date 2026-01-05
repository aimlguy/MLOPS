"""
Progressive Model Pipeline State Manager

Tracks the current state of the progressive model deployment pipeline:
- baseline (worst) → improved → best
- Only trains next model when triggered
- Only deploys if better than current
"""

import json
import os
from datetime import datetime
from typing import Literal

ModelStage = Literal["baseline", "improved", "best"]

STATE_FILE = "pipeline_state.json"

class PipelineState:
    def __init__(self):
        self.current_stage: ModelStage = "baseline"
        self.current_model_auc: float = 0.0
        self.deployment_history: list = []
        self.last_updated: str = datetime.utcnow().isoformat()
        
    def load(self):
        """Load state from file"""
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                self.current_stage = data.get("current_stage", "baseline")
                self.current_model_auc = data.get("current_model_auc", 0.0)
                self.deployment_history = data.get("deployment_history", [])
                self.last_updated = data.get("last_updated", datetime.utcnow().isoformat())
        return self
    
    def save(self):
        """Save state to file"""
        data = {
            "current_stage": self.current_stage,
            "current_model_auc": self.current_model_auc,
            "deployment_history": self.deployment_history,
            "last_updated": self.last_updated
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_next_stage(self) -> ModelStage | None:
        """Get the next model stage to train"""
        if self.current_stage == "baseline":
            return "improved"
        elif self.current_stage == "improved":
            return "best"
        else:
            return None  # Already at best
    
    def should_deploy(self, new_auc: float) -> bool:
        """Check if new model should be deployed (better than current)"""
        return new_auc > self.current_model_auc
    
    def record_deployment(self, stage: ModelStage, auc: float):
        """Record a successful deployment"""
        self.current_stage = stage
        self.current_model_auc = auc
        self.deployment_history.append({
            "stage": stage,
            "auc": auc,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.last_updated = datetime.utcnow().isoformat()
        self.save()
    
    def reset(self):
        """Reset pipeline to baseline"""
        self.current_stage = "baseline"
        self.current_model_auc = 0.0
        self.last_updated = datetime.utcnow().isoformat()
        self.save()
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "current_stage": self.current_stage,
            "current_model_auc": self.current_model_auc,
            "next_stage": self.get_next_stage(),
            "can_progress": self.get_next_stage() is not None,
            "deployment_history": self.deployment_history,
            "last_updated": self.last_updated
        }

# Singleton instance
_state = None

def get_pipeline_state() -> PipelineState:
    """Get or create pipeline state singleton"""
    global _state
    if _state is None:
        _state = PipelineState().load()
    return _state

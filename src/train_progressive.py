"""
Progressive Model Training Script

Trains a specific model stage (baseline, improved, or best) based on command line argument.
Used by the progressive deployment pipeline.
"""

import sys
import os
import argparse
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.train_baseline import train_baseline_model
from src.train_improved import train_improved_model
from src.train_best import train_best_model

def main():
    parser = argparse.ArgumentParser(description="Train a specific model stage")
    parser.add_argument(
        "--stage",
        type=str,
        required=True,
        choices=["baseline", "improved", "best"],
        help="Model stage to train"
    )
    parser.add_argument(
        "--auto-promote",
        action="store_true",
        help="Automatically promote if better"
    )
    
    args = parser.parse_args()
    
    data_path = "data/raw/noshow.csv"
    
    print(f"\n{'='*50}")
    print(f"Training {args.stage.upper()} model")
    print(f"{'='*50}\n")
    
    # Train the appropriate model
    metrics_result = {}
    if args.stage == "baseline":
        metrics_result = train_baseline_model(data_path, auto_promote=args.auto_promote)
    elif args.stage == "improved":
        metrics_result = train_improved_model(data_path, auto_promote=args.auto_promote)
    elif args.stage == "best":
        metrics_result = train_best_model(data_path, auto_promote=args.auto_promote)
    else:
        raise ValueError(f"Unknown stage: {args.stage}")
    
    # Output metrics in parseable format
    print("\n__METRICS_OUTPUT__")
    print(json.dumps(metrics_result))
    print("__METRICS_END__")
    
    return metrics_result
    
    print(f"\n{'='*60}")
    print(f"TRAINING {args.stage.upper()} MODEL")
    print(f"{'='*60}\n")
    
    # Train the specified stage
    if args.stage == "baseline":
        metrics = train_baseline(auto_promote=args.auto_promote)
    elif args.stage == "improved":
        metrics = train_improved(auto_promote=args.auto_promote)
    elif args.stage == "best":
        metrics = train_best(auto_promote=args.auto_promote)
    
    # Output metrics in JSON format for parsing
    import json
    print("\n__METRICS_OUTPUT__")
    print(json.dumps(metrics))
    print("__METRICS_END__")
    
    return metrics

if __name__ == "__main__":
    main()

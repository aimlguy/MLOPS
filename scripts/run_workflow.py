import subprocess
import sys

def run_command(command):
    """Executes a command and prints its output in real-time."""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    rc = process.poll()
    return rc

def main():
    """Runs the complete DVC pipeline."""
    print("🚀 Starting complete MLOps workflow...")
    
    # The `dvc repro` command will automatically run all stages defined in dvc.yaml
    # in the correct order, skipping any stages where dependencies haven't changed.
    return_code = run_command("dvc repro")
    
    if return_code != 0:
        print("\n❌ DVC pipeline failed.")
        sys.exit(return_code)
        
    print("\n✅ Complete MLOps workflow finished successfully!")
    print("📊 Check the 'reports' directory for evaluation results and 'mlruns' for model artifacts.")

if __name__ == "__main__":
    main()

import subprocess
import time
import sys
import os

def launch():
    print("Launching DrawffyFish...")
    
    # DYNAMIC PATH: Automatically finds the folder this script is sitting in
    project_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(project_dir, "main.py")
    
    while True:
        try:
            # Executes main.py explicitly using the dynamic directory path
            process = subprocess.Popen(
                [sys.executable, main_script], 
                cwd=project_dir
            )
            process.wait()
            
        except KeyboardInterrupt:
            print("\nShutting down bot process.")
            break
        except Exception as e:
            print(f"Process crashed: {e}. Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    launch()

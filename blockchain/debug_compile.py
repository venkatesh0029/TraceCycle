
import subprocess
import sys

try:
    # Run the command and capture both stdout and stderr
    output = subprocess.check_output("npx hardhat compile", shell=True, stderr=subprocess.STDOUT)
    with open("debug_log.txt", "w", encoding="utf-8") as f:
        f.write(output.decode('utf-8', errors='ignore'))
    print("Output written to debug_log.txt")
except subprocess.CalledProcessError as e:
    with open("debug_log.txt", "w", encoding="utf-8") as f:
        f.write(e.output.decode('utf-8', errors='ignore'))
    print("Command failed, output written to debug_log.txt")

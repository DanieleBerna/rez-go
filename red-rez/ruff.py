import subprocess
import os
subprocess.call("set.exe TEST_ENV_VAR=percorso/casuale", shell=True)

subprocess.call("echo %TEST_ENV_VAR%",shell=True)

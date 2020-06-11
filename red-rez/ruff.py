import os
import subprocess
os.environ["TEST_KEY"] = "my test key"
env = os.environ.copy()
subprocess.Popen(["echo", "%TEST_KEY%"], shell=True, env=env).wait()
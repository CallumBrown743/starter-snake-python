import subprocess
for x in range(100):
	response = subprocess.check_output(["engine", "create", "-c", "snake-config.json"])
	subprocess.check_output(["engine", "run", "-g", str(response)[10:46]])
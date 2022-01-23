import subprocess, pkg_resources
packages = [dist.project_name for dist in pkg_resources.working_set]
subprocess.call("pip install --upgrade " + ' '.join(packages), shell=True)

import os
import subprocess


class V2ctl():

    def __init__(self, root_path):
        self.root_path = root_path
        self.p = None

    def stop(self):
        if self.p is not None:
            self.p.kill()

    def is_running(self):
        if self.p is not None and self.p.poll() is None:
            return True
        else:
            return False

    def statue(self):
        if self.is_running():
            return 'active (running)'
        else:
            return 'inactive (dead)'

    def restart(self):
        self.stop()
        self.start()

    def start(self):
        path = self.root_path + os.sep + 'v2ray-core' + os.sep
        log_path = self.root_path + os.sep + 'logs' + os.sep + 'v2.log'
        run_code = path + 'v2ray' + ' --config ' + path + 'config.json'
        with open(log_path, 'w+') as f:
            self.p = subprocess.Popen(run_code, shell=True, stdout=f)

import sys
import time
import pexpect
from synth_client import ConfigurableJackSynth

class JalvSynth(ConfigurableJackSynth):

    def __init__(self, config):
        super(JalvSynth, self).__init__(
            config['lv2_plugins'],
            config)
        self.jack_name = None

    def _get_jack_name(self):
        return self.jack_name

    def _start_process(self, plugin):
        process = pexpect.spawn('jalv {}'.format(plugin['url']))
        process.logfile = sys.stdout

        # extract jack name from stdin
        process.expect('JACK Name:')
        self.jack_name = process.readline().strip()
        time.sleep(1)
        process.expect('>')
        return process

    def _stop(self, process):
        process.terminate()

    def _switch_patch(self, patch):
        self.deactivate()
        self._activate(patch)

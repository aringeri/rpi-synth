import sys
import pexpect
from synth_client import ConfigurableJackSynth

class SetBFreeSynth(ConfigurableJackSynth):

    def __init__(self, config):
        super(SetBFreeSynth, self).__init__(['default'], config)

    def _get_jack_name(self):
        return 'setBfree'

    def _start_process(self, patch):
        command = 'setBfree -c {} jack.connect=\'\''.format(self.config['setBfree_midi_config'])
        process = pexpect.spawn(command)
        process.logfile = sys.stdout
        process.expect('All systems go')

        return process

    def _stop(self, process):
        process.sendcontrol('c')
        process.expect(pexpect.EOF)
        process.terminate()

    def _switch_patch(self, patch):
        pass

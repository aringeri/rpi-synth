import glob
import sys
import pexpect
from synth_client import ConfigurableJackSynth

class FluidsynthSynth(ConfigurableJackSynth):
    __cores = 3

    def __init__(self, config):
        super(FluidsynthSynth, self).__init__(
            self.__load_soundfonts(config['soundfont_dir']),
            config)
        self._patch_id = 0

    def __load_soundfonts(self, soundfont_dir):
        fonts = [font for font in glob.glob(soundfont_dir + '/*.sf2')]
        fonts.sort()
        return fonts

    def _get_jack_name(self):
        return 'fluidsynth'

    def _start_process(self, active_soundfont):
        command = 'fluidsynth -a jack -m jack -p {} -o synth.cpu-cores={} {}'.format(
            self._get_jack_name(),
            self.__cores,
            active_soundfont)
        process = pexpect.spawn(command)
        process.logfile = sys.stdout
        process.expect('Type \'help')
        self._patch_id = 1

        return process

    def _stop(self, process):
        process.sendline('quit')
        process.expect('cheers')
        process.close()

    def _switch_patch(self, next_font):
        if self._patch_id > 0:
            self._get_process().sendline('unload {}'.format(self._patch_id))

        self._get_process().sendline('load {}'.format(next_font))
        self._get_process().expect('loaded')
        self._patch_id += 1

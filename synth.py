#!/usr/bin/python
import time
import sys
import pexpect
from controller import SynthController
from fluidsynth_synth import FluidsynthSynth
from set_b_free_synth import SetBFreeSynth
from jalv_synth import JalvSynth
from connection_manager import ConnectionManager

# regular expression for midi keyboard ports (jack)
keyboard_ports = ['a2j:.*A-PRO 1', '.*UM-ONE.*']

config = {
    'keyboard.midi.ports': keyboard_ports,
    # midi port to control bank/synth changes
    'bank_control.midi.ports' : keyboard_ports,
    # midi port to control looping
    'loop.midi.port'     : 'LPD8',
    # path to the sooperlooper midi mapping configuration file
    'sooperlooper_midi_cfg' : '/home/pi/sooperlooper/SooperLooper-midi.slb',
    # path to soundfont (.sf2) files
    'soundfont_dir'      : '/home/pi/soundfonts',
    # list of installed lv2 plugins
    'lv2_plugins'        : [
        {'url' : 'http://moddevices.com/plugins/mda/EPiano'},
        {'url' : 'http://moddevices.com/plugins/mda/JX10'},
        {'url' : 'https://github.com/dcoredump/dexed.lv2'},
        {'url' : 'http://tytel.org/helm'}
    ],
    # poth to setBfree midi mapping configuration file
    'setBfree_midi_config' : '/home/pi/setBfree/a-pro.cfg',
    # audio ports to route synth outputs
    'audio_out' : ['system']
}
connection_manager = ConnectionManager('synth')
config['connection_manager'] = connection_manager

sooperlooper = pexpect.spawn('sooperlooper -m {}'.format(config['sooperlooper_midi_cfg']))
sooperlooper.logfile = sys.stdout
sooperlooper.expect('OSC server URI')
time.sleep(1)
connection_manager.autoconnect_midi(config['loop.midi.port'], 'sooperlooper')
connection_manager.connect_audio('sooperlooper', 'system')

config['audio_out'].append('sooperlooper')

synths = [JalvSynth(config), FluidsynthSynth(config), SetBFreeSynth(config)]
synth_controller = SynthController(synths, config)
synth_controller.start()

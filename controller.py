import sys
import time
from multiprocessing.pool import ThreadPool
import pexpect
from mididings import *

class SynthController(object):

    def __init__(self, synths, config):
        assert synths, 'At least one synth client required.'
        self._synths = synths
        self.config = config
        self._pool = ThreadPool(processes=1)
        self._active_synth = None

    def start(self):
        midi_ports = self.config['bank_control.midi.ports']

        config(
            backend='jack',
            in_ports=[
                ('midi_in',) + tuple(midi_ports)
            ]
        )

        self._active_synth = self._synths[0]
        self._active_synth.activate()

        for j_port in midi_ports:
            self.config['connection_manager'].autoconnect_midi(
                j_port
                , 'mididings'
                , connect_now=False)
        run([
            CtrlFilter(32) >> Call(self._handle_bank_change)
            , self._shutdown_filter() >> Call(self._shutdown)
            , self._reboot_filter() >> Call(self._reboot)
        ])

    def _handle_bank_change(self, ev):
        val = ev.value
        num_synths = len(self._synths)
        if val < num_synths:
            if self._synths[val] != self._active_synth:
                self._synth_change(val)
        elif val - num_synths < self._active_synth.num_patches():
            self._patch_change(val - num_synths)
        else:
            print 'bank change out of range: {}'.format(val)

    def _synth_change(self, next_id):
        assert 0 <= next_id < len(self._synths)
        def synth_change_f():
            self._active_synth.deactivate()
            self._active_synth = self._synths[next_id]

            self._active_synth.activate()
        self._pool.apply_async(synth_change_f)

    def _patch_change(self, next_id):
        self._pool.apply_async(
            self._active_synth.set_patch,
            [next_id])

    def _shutdown_filter(self):
        return self._two_button_filter(SYSRT_STOP, SYSRT_START)

    def _two_button_filter(self, btn1, btn2):
        class nonlocal:
            stop_t = 0
            start_t = 0

        def both_pressed(ev):
            now = time.time()
            if ((ev.type == btn1 and now - nonlocal.start_t < 0.1)
                    or (ev.type == btn2 and now - nonlocal.stop_t < 0.1)):
                return ev

            if ev.type == btn1:
                nonlocal.stop_t = now
            elif ev.type == btn2:
                nonlocal.start_t = now

            return None

        return Filter(btn1 | btn2) >> Process(both_pressed)

    def _shutdown(self, ev):
        print 'shutting down'
        self._active_synth.deactivate()
        print pexpect.run('sudo shutdown -P now')
        sys.exit()

    def _reboot_filter(self):
        return self._two_button_filter(SYSRT_START, SYSRT_CONTINUE)

    def _reboot(self, ev):
        print 'rebooting'
        self._active_synth.deactivate()
        print pexpect.run('sudo reboot')
        sys.exit()

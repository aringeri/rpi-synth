from abc import ABCMeta, abstractmethod

class SynthClient(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def num_patches(self):
        pass

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def deactivate(self):
        pass

    @abstractmethod
    def set_patch(self, patch_id):
        pass

class SynthProcess(SynthClient):

    def __init__(self, patches):
        super(SynthProcess, self).__init__()
        self._process = None
        self._active_patch = None
        self._patches = patches

    def _get_process(self):
        return self._process

    def num_patches(self):
        return len(self._patches)

    def activate(self):
        if self._process is None:
            self._activate(self._patches[0])

    def _activate(self, active_patch):
        self._active_patch = active_patch
        self._process = self._start(self._active_patch)

    @abstractmethod
    def _start(self, active_patch):
        pass

    def deactivate(self):
        if self._process != None:
            self._stop(self._process)
            self._active_patch = None
            self._process = None

    @abstractmethod
    def _stop(self, process):
        pass

    def set_patch(self, patch_id):
        assert 0 <= patch_id < len(self._patches)
        if self._active_patch != self._patches[patch_id]:
            self._switch_patch(self._patches[patch_id])
            self._active_patch = self._patches[patch_id]

    @abstractmethod
    def _switch_patch(self, patch):
        pass

class JackSynth(SynthProcess):

    def _start(self, active_patch):
        process = self._start_process(active_patch)
        self._connect_jack_ports()
        return process

    @abstractmethod
    def _start_process(self, active_patch):
        pass

    def _connect_jack_ports(self):
        manager = self._get_connection_manager()
        for midi_in in self._get_midi_in_ports():
            manager.autoconnect_midi(midi_in, self._get_jack_name())

        for audio_out in self._get_audio_out_ports():
            manager.connect_audio(self._get_jack_name(), audio_out)

    @abstractmethod
    def _get_connection_manager(self):
        pass

    @abstractmethod
    def _get_jack_name(self):
        pass

    @abstractmethod
    def _get_midi_in_ports(self):
        pass

    @abstractmethod
    def _get_audio_out_ports(self):
        pass

class ConfigurableJackSynth(JackSynth):

    def __init__(self, patches, config):
        super(ConfigurableJackSynth, self).__init__(patches)
        self.config = config

    def _get_connection_manager(self):
        return self.config['connection_manager']

    def _get_midi_in_ports(self):
        return self.config['keyboard.midi.ports']

    def _get_audio_out_ports(self):
        return self.config['audio_out']

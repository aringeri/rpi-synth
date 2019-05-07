from collections import defaultdict
from multiprocessing.pool import ThreadPool
import jack

def pairwise(lst):
    return zip(lst[0::2], lst[1::2])

class ConnectionManager(object):

    def __init__(self, name):
        self._auto_midi = defaultdict(set)
        self._pool = ThreadPool(processes=1)
        self._client = jack.Client(name)
        self._client.set_port_registration_callback(self.port_change)
        self._client.activate()

    def port_change(self, port, port_created):
        if (port_created
                and port.is_midi
                and port.is_output):
            #lookup ports that need auto connection
            registered = dict([(src_port.name, tgt_regex)
                               for (src_regex, tgt_regex) in self._auto_midi.iteritems()
                               for src_port in self._client.get_ports(src_regex,
                                                                      is_output=True,
                                                                      is_midi=True)
                              ])

            #schedule a connection task with registered targets
            if port.name in registered.keys():
                for tgt_regex in registered[port.name]:
                    for tgt_port in self._client.get_ports(tgt_regex, is_input=True, is_midi=True):
                        self._pool.apply_async(self._client.connect, [port, tgt_port])

    def autoconnect_midi(self, source, target, connect_now=True):
        if connect_now:
            self.connect_midi(source, target)
        self._auto_midi[source].add(target)

    def connect_midi(self, source, target):
        src_ports = self._client.get_ports(source, is_output=True, is_midi=True)
        tgt_ports = self._client.get_ports(target, is_input=True, is_midi=True)

        for i_port in src_ports:
            for o_port in tgt_ports:
                self._client.connect(i_port, o_port)

    def connect_audio(self, source, target):
        src_ports = self._client.get_ports(source, is_output=True, is_audio=True)
        tgt_ports = self._client.get_ports(target, is_input=True, is_audio=True)

        if len(src_ports) == 1:
            src_port = src_ports[0]
            for o_port in tgt_ports:
                self._client.connect(src_port, o_port)
        else:
            ports = zip(pairwise(src_ports), pairwise(tgt_ports))
            for ((src_left, src_right), (tgt_left, tgt_right)) in ports:
                self._client.connect(src_left, tgt_left)
                self._client.connect(src_right, tgt_right)

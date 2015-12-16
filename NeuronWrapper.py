import sys
import os.path

from neuron import h
from helper.myneuron import MyNeuron

__author__ = 'Sergey Khayrulin'


# this 3 names of neurons it's temporary in future we will load all neurons directly from hoc file
AVM = 'AVM'
ALML = 'ALML'
ALMR = 'ALMR'

v = 'v'
v_pre = 'v_pre'
v_post = 'v_post'
i_syn = 'i_syn'
t = 't'
paramVec = [v]


class NrnSimulator:
    """
    NEURON wrapper init and run
    model described on hoc ito NEURON simulator
    """

    def __init__(self, model_name, tstop=20.0):
        if model_name != "":
            if not (os.path.isfile(model_name)):
                raise AttributeError(
                    u"File: {0:s} doesn't exist please check the path to the file or name of file".format(model_name))
            h.load_file(model_name)
            h.init()
            h.tstop = tstop
            self.out_data = {}
            self.neuronsnames = []
            self.neurons = {}
            self.__find_all_neurons()
            if len(self.neuronsnames) == 0:
                raise RuntimeError(u"In File: {0:s} with model no any neurons has been found please check the "
                                   u"the file".format(model_name))
            for name in self.neuronsnames:
                self.neurons[name] = MyNeuron(name)
            # Initialization of segments and data arrays
            for k, val in self.neurons.iteritems():
                val.init_sections(h, paramVec)
        else:
            raise ValueError("Name of file with Model shouldn't be empty")

    def __update_data(self):
        for k, val in self.neurons.iteritems():
            val.update_seg_data(paramVec)

    def one_step(self):
        """

        :rtype : object
        """
        if h.t < h.tstop:
            h.advance()
            self.__update_data()
        else:
            print 'Simulation is finished'
            sys.exit(0)

    def __find_all_neurons(self):
        """
        Serach neurons names from hoc segment name
        """
        for h_sec in h.allsec():
            section_name = h_sec.name()
            index = section_name.find('_soma')
            if index != -1:
                self.neuronsnames.append(section_name[0:index])
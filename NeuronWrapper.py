import sys
import os.path


from neuron import gui #TODO remove this than
from helper.myneuron import MyNeuron

__author__ = 'Sergey Khayrulin'

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
            from neuron import h
            h.finitialize()
            h.load_file("stdrun.hoc")
            h.load_file(1, model_name) # http://www.neuron.yale.edu/neuron/static/new_doc/programming/dynamiccode.html#
            h.init()
            h.tstop = tstop
            self.out_data = {}
            self.neurons_names = []
            self.neurons = {}
            self.__find_all_neurons()
            if len(self.neurons_names) == 0:
                raise RuntimeError(u"In File: {0:s} with model no any neurons has been found please check the "
                                   u"the file".format(model_name))
            print self.neurons_names
            for name in self.neurons_names: #TODO put check that we haven't added this neuron yet in dictionary neurons
                self.neurons[name] = MyNeuron(name, index=self.neurons_names.index(name))
            # Initialization of segments and data arrays
            for k, val in self.neurons.iteritems():
                val.init_sections(h, paramVec)
            self.__index_sub_segments()
        else:
            raise ValueError("Name of file with Model shouldn't be empty")

    def __update_data(self):
        for k, val in self.neurons.iteritems():
            val.update_sec_data(paramVec)

    def one_step(self):
        """
        Make one step of NEURON simulation
        """
        from neuron import h
        if h.t < h.tstop:
            h.advance()
            self.__update_data()
        else:
            print 'Simulation is finished'
            sys.exit(0)

    def __find_all_neurons(self):
        """
        Search neurons names from hoc segment name
        """
        from neuron import h
        for h_sec in h.allsec():
            section_name = h_sec.name()
            index = section_name.find('_')
            if index != -1:
                self.neurons_names.append(section_name[0:index])

    def get_time(self):
        from neuron import h
        return h.t

    def __index_sub_segments(self):
        unique_indexes = []
        index = 0
        for k, v in self.neurons.iteritems():
            for sec in v.sections:
                for sub_sec in sec.sub_sections:
                    if not(index in unique_indexes):
                        unique_indexes.append(index)
                    else:
                        index += 1
                    sub_sec.index = index

    def finish(self):
        """
        Do nothing yet
        """
        pass

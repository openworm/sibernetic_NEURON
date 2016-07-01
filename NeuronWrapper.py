# The MIT License (MIT)
#
# Copyright (c) 2011, 2013 OpenWorm.
# http://openworm.org
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the MIT License
# which accompanies this distribution, and is available at
# http://opensource.org/licenses/MIT
#
# Contributors:
#      OpenWorm - http://openworm.org/people.html
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#pass
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
# USE OR OTHER DEALINGS IN THE SOFTWARE.
from __future__ import with_statement

import os.path
from neuron import gui
from helper.myneuron import MyNeuron

__author__ = 'Sergey Khayrulin'

v = 'v'
v_pre = 'v_pre'
v_post = 'v_post'
i_syn = 'i_syn'
t = 't'
paramVec = [v, v_pre, v_post, i_syn]


class NrnSimulator:
    """
    NEURON wrapper init and run
    model described on hoc into NEURON simulator
    """

    def __init__(self, model_name, tstop=20.0):
        if model_name != "":
            if not (os.path.isfile(model_name)):
                raise AttributeError(
                    u"File: {0:s} doesn't exist please check the path to the file or name of file".format(model_name))
            from neuron import h
            h.load_file("nrngui.hoc")
            h.load_file(model_name) # http://www.neuron.yale.edu/neuron/static/new_doc/programming/dynamiccode.html#
            h.init()
            h.tstop = tstop
            self.out_data = {}
            self.neuron_sections = {}
            self.neurons = {}
            self.__find_all_neurons()
            if len(self.neuron_sections.keys()) == 0:
                raise RuntimeError(u"In File: {0:s} with model no any neurons has been found. Please check the "
                                   u"the file".format(model_name))
            # Initialization of segments and data arrays
            for n_name, val in self.neuron_sections.iteritems():
                self.neurons[n_name] = MyNeuron(n_name, index=self.neuron_sections.keys().index(n_name))
                self.neurons[n_name].init_sections(h, paramVec, self.neuron_sections[n_name])
            self.__index_sub_segments()
            self.simulation_speed = 1
            #sibernetic part here we will store sections names from which we want to get info about voltage and so one
            self.sibernetic_sections = {}
        else:
            raise ValueError("Name of file with Model shouldn't be empty")

    def __update_data(self):
        for k, val in self.neurons.iteritems():
            val.update_sec_data(paramVec)

    def get_dt(self):
        from neuron import h
        return h.dt

    def set_dt(self, dt):
        if dt != 0.0:
            from neuron import h
            h.dt = dt

    def gen_sib_sec_list(self, s_sections=[]):
        if len(s_sections) == 0:
            return
        for sec in s_sections:
            for neuron in self.neurons.values():
                if sec in neuron.sections.keys():
                    neuron.selected = True
                    neuron.sections[sec].selected = True
                    neuron.sections[sec].sub_sections[1].selected = True
                    self.sibernetic_sections[neuron.name] = sec

    def one_step(self):
        """
        Make one step of NEURON simulation
        """
        from neuron import h
        if h.t < h.tstop:
            for i in xrange(self.simulation_speed):
                h.advance()
            self.__update_data()
        else:
            #print 'Simulation is finished'
            #sys.exit(0)
            pass
        result = []
        for neuron_name, sec in self.sibernetic_sections.iteritems():
            if sec in self.neurons[neuron_name].sections.keys():
                result.append(self.neurons[neuron_name].get_voltage(sec))
        return result

    def __find_next_layer(self, sections, first_iter):
        ret_sections = []
        if first_iter:
            ret_sections = [s for s in sections if s.parent is None]
        else:
            for s in sections:
                for neuron_n, val in self.neuron_sections.iteritems():
                    if s.parent.name() in val:
                        s.neuron_n = neuron_n
                        ret_sections.append(s)
                        break
        return ret_sections

    def __find_all_neurons(self):
        """
         Search neurons names from hoc section name
         First it generate list of sections with some info like hoc section pointer parent
         hoc section pointer if it has other case it equal to None. Than it run loop in which it runs function
         __find_next_layer which is generate list of section parent section of which is in self.neuron_sections yet
         do that until len(sections_) not equal to zero
        """
        class Sec:
            def __init__(self):
                self.parent = None
                self.sec = None
                self.neuron_n = ''
        from neuron import h
        sections_ = []
        iteration = 0
        for h_sec in h.allsec():
            s = Sec()
            s.sec = h_sec
            if h.SectionRef().has_parent():
                s.parent = h.SectionRef().parent
            sections_.append(s)
        while len(sections_) != 0:
            temp_sections = self.__find_next_layer(sections_, iteration == 0)
            if iteration == 0:
                for i in xrange(len(temp_sections)):
                    current_neuron_name = 'Neuron_' + str(i)
                    temp_sections[i].neuron_n = current_neuron_name
                    self.neuron_sections[current_neuron_name] = [temp_sections[i].sec.name()]
            else:
                for i in xrange(len(temp_sections)):
                    self.neuron_sections[temp_sections[i].neuron_n].append(temp_sections[i].sec.name())
            sections_ = [s for s in sections_ if s not in temp_sections]
            iteration += 1
        print 'Number of founded neurons is %s list is %s'%(len(self.neuron_sections.keys()), self.neuron_sections.keys())

    def get_time(self):
        from neuron import h
        return h.t

    def __index_sub_segments(self):
        index = 0
        a = []
        for neuron in self.neurons.values():
            for sec in neuron.sections.values():
                for sub_sec in sec.sub_sections:
                    a.append(index)
                    sub_sec.index = index
                    index += 1
        print index

    def add_stim(self, amp, delay, dur, n_name=''):
        """
        Add stimul into selected section
        :param amp:
        :param delay:
        :param dur:
        :param n_name:
        :param sec_name:
        """
        #TODO describe all in detail
        from neuron import h
        selected_neurons = []
        if n_name =='':
            selected_neurons = [neuron for n_name, neuron in self.neurons.iteritems() if neuron.selected]
        elif n_name != '':
            selected_neurons.append(self.neurons[n_name])
        if len(selected_neurons) == 0:
            print 'No selected neurons. Please select.'
            return
        for neuron in selected_neurons:
            stim = h.IClamp(0.5, neuron.get_selected_section().h_sec)
            stim.amp = amp
            stim.delay = delay
            stim.dur = dur

    def add_synaps(self, sec_id1, sec_id2):
        pass

    def finish(self):
        """
        Do nothing yet
        """
        pass

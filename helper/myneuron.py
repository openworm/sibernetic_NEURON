import re
import math

__author__ = 'Serg Khayrulin'


class SubSegment:
    def __init__(self, parent=None):
        """

        :type self: object
        """
        self.start_x = 0
        self.start_y = 0
        self.start_z = 0
        self.end_x = 0
        self.end_y = 0
        self.end_z = 0
        self.diam = 0
        self.h = 0
        self.params = {}
        self.index = -1
        self.selected = False
        self.parent = parent

    def calc_h(self):
        self.h = math.sqrt(math.pow(self.start_x - self.end_x, 2) + math.pow(self.start_y - self.end_y, 2) +
                           math.pow(self.start_z - self.end_z, 2))

    def get_param(self, p_name):
        return self.params[p_name]


class Segment:
    def __init__(self, index=-1, name='', parent=None):
        self.index = index
        self.signal = -1
        self.color = 0
        self.name = name
        self.sub_sec = []
        self.selected = False
        self.parent = parent

    def init_segment(self, h, params):
        self.nseg = h.cas().nseg
        self.h_seg = h.cas()
        current_lenght = 0.0
        len_diff_segment = self.h_seg.L/self.nseg
        for i in range(int(h.n3d()) - 1):
            m_s = SubSegment(self)
            m_s.start_x = h.x3d(i)
            m_s.start_y = h.y3d(i)
            m_s.start_z = h.z3d(i)
            m_s.end_x = h.x3d(i + 1)
            m_s.end_y = h.y3d(i + 1)
            m_s.end_z = h.z3d(i + 1)
            m_s.diam = h.diam3d(i)
            m_s.calc_h()
            current_lenght += m_s.h
            x_info = int(current_lenght/len_diff_segment)
            self.__update_data(params, m_s, float(x_info)/float(self.nseg))
            self.sub_sec.append(m_s)

    def __update_data(self, params, m_s, n=-1):
        """
        Initializing parameters what we want to get from NEURON simulation
        :param params: parameters interesting
        :param m_s: current subsegmet
        :param n: number of current subsection in section it defines by nseg
        """
        for p in params:
            if p in m_s.params:
                m_s.params[p] = (self.h_seg(m_s.params[p][1])._ref_v[0], m_s.params[p][1])
            elif n != -1:
                m_s.params[p] = (self.h_seg(n)._ref_v[0], n)
            else:
                raise RuntimeError('Problem with initalization')
            # TODO find mode suitable way how to do it

    def update_data(self, params):
        for s_sec in self.sub_sec:
            self.__update_data(params, s_sec)


class MyNeuron:
    def __init__(self, name="", index=0):
        self.name = name
        self.section = []
        self.selected = False
        self.index = index

    def init_sections(self, h, params):
        """
        Select from list of sections
        only sections for particular helper
        fill list of section ids

        :param h: hocObject
        """
        pattern = '^' + self.name + '_.*'
        nrn_pattern = re.compile(pattern)
        index = 0
        for h_sec in h.allsec():
            section_name = h_sec.name()
            if not (nrn_pattern.search(section_name) is None):
                s = Segment(index, section_name, self)
                s.init_segment(h, params)
                self.section.append(s)
            index += 1

    def update_seg_data(self, params):
        """

        :rtype : object
        """
        for s in self.section:
            s.update_data(params)

    def turn_off_selection(self):
        self.selected = False
        for sec in self.section:
            sec.selected = False
            for sub_sec in sec.sub_sec:
                sub_sec.selected = False

    def get_selected_section(self):
        if not self.selected:
            return None
        for sec in self.section:
            if sec.selected:
                for sub_sec in sec.sub_sec:
                    if sub_sec.selected:
                        return sub_sec

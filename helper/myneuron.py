__author__ = 'Serg Khayrulin'

import re
import math


class SubSegment:
    def __init__(self):
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

    def calc_h(self):
        self.h = math.sqrt(math.pow(self.start_x - self.end_x, 2) + math.pow(self.start_y - self.end_y, 2) + math.pow(self.start_z - self.end_z, 2))

    def get_param(self, p_name):
        return self.params[p_name]


class Segment:
    def __init__(self, index=-1, name=''):
        self.index = index
        self.signal = -1
        self.color = 0
        self.name = name
        self.sub_seg = []

    def init_segment(self, h, params):
        self.nseg = h.cas().nseg
        self.h_seg = h.cas()
        current_lenght = 0.0
        len_diff_segment = self.h_seg.L/self.nseg
        for i in range(int(h.n3d()) - 1):
            m_s = SubSegment()
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
            self.__update_data(params, m_s, float(x_info)/float(self.nseg)) # float(float(i) / (float(self.nseg)))
            self.sub_seg.append(m_s)

    def __update_data(self, params, m_s, n=-1):
        """
        Initializing parameters what we want get from NEURON simulation

        :param params: parameters interesting
        :param m_s: current subsegmet
        :param n: number of current subsegment in segment. it is defined by nseg
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
        for s_seg in self.sub_seg:
            #i = float(float(self.sub_seg.index(s_seg))/float(self.nseg))
            self.__update_data(params, s_seg)


class MyNeuron:
    def __init__(self, name="", index=0):
        self.name = name
        self.segment = []
        self.selected = False
        self.index = index

    def init_segments(self, h, params):
        """
        Select from list of segments
        only segments for particular helper
        fill list of segment ids

        :param h: hocObject
        """
        pattern = '^' + self.name + '_.*'
        nrn_pattern = re.compile(pattern)
        index = 0
        for h_seg in h.allsec():
            segment_name = h_seg.name()
            if not (nrn_pattern.search(segment_name) is None):
                s = Segment(index, segment_name)
                s.init_segment(h, params)
                self.segment.append(s)
            index += 1

    def update_seg_data(self, params):
        """

        :rtype : object
        """
        for s in self.segment:
            s.update_data(params)

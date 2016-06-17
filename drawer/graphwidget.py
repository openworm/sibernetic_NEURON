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
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
# USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import print_function

from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backends import qt4_compat

use_pyside = qt4_compat.QT_API == qt4_compat.QT_API_PYSIDE

import matplotlib.animation as animation
from matplotlib.pyplot import *

if use_pyside:
    from PySide.QtCore import *
    from PySide.QtGui import *
else:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *


class NSGraphWidget(QWidget):
    def __init__(self, nrn, time_limit, parent=None):
        super(NSGraphWidget, self).__init__(parent)
        self.nrn = nrn
        self.time_limit = time_limit
        self.create_main_frame()
        self.on_draw()
        self.legend_list = []

    def create_main_frame(self):
        mainLayout = QHBoxLayout()
        self.main_frame = QWidget()

        self.fig = Figure((7.0, 7.0), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()

        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        self.canvas.mpl_connect('key_press_event', self.on_key_press)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)  # the matplotlib canvas
        vbox.addWidget(self.mpl_toolbar)
        self.main_frame.setLayout(vbox)
        mainLayout.addWidget(self.main_frame)
        self.setLayout(mainLayout)

    def run(self, data):
        # update the data
        t, y, names = data
        self.xdata.append(t)
        self.ydata.append(y)
        xmin, xmax = self.axes.get_xlim()
        ymin, ymax = self.axes.get_ylim()
        # self.lines = []
        if t >= xmax:
            self.axes.set_xlim(xmin, 2 * xmax)
            self.axes.figure.canvas.draw()
        if y[0] >= ymax:
            self.axes.set_ylim(xmin, 2 * ymax)
            self.axes.figure.canvas.draw()
        for i in xrange(len(self.ydata[-1])):
            if i == len(self.ydata[-1]) - 1 and i + 1 < len(self.lines):
                self.lines.pop(i)
                break
            res = []
            for j in xrange(len(self.ydata)):
                if i < len(self.ydata[j]):
                    res.append(self.ydata[j][i])
            if i >= len(self.lines):
                line, = self.axes.plot([], [], lw=1)
                self.lines.append(line)
            self.lines[i].set_data(self.xdata[len(self.xdata) - len(res):], res)
        legend = self.axes.legend(self.lines, names, fancybox=True)
        for label in legend.get_texts():
            label.set_fontsize('small')
        # self.legend_list.append(legend(self.lines, ["Label 1"]))
        return self.lines

    def on_draw(self):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        self.lines = []
        self.texts = []
        self.xdata, self.ydata = [], []
        self.ani = animation.FuncAnimation(self.fig, self.run, self.data_gen, blit=False, interval=10, repeat=False,
                                           init_func=self.init)
        self.canvas.draw()

    def data_gen(self, t=0):
        while self.nrn.get_time() < self.time_limit:
            sub_sec = None
            result = []
            sec_names = []
            param_name = ['v']
            for neuron_name, n in self.nrn.neurons.iteritems():
                sec_name, sub_sec = n.get_selected_sub_section()
                if sub_sec != None:
                    result.append(sub_sec.get_param('v')[0])
                    sec_names.append('v ' + neuron_name + ' ' + sec_name)
            if len(result) != 0:
                yield self.nrn.get_time(), result, sec_names
            else:
                yield 0, [-70.0], sec_names

    def on_key_press(self, event):
        print('you pressed', event.key)
        # implement the default mpl key press events described at
        # http://matplotlib.org/users/navigation_toolbar.html#navigation-keyboard-shortcuts
        key_press_handler(event, self.canvas, self.mpl_toolbar)

    def init(self):
        self.axes.set_title('Voltage in selected sections',fontsize=16, fontweight='bold')
        self.axes.set_xlabel('Time (s)')
        self.axes.set_ylabel('Voltage (V)')
        self.axes.set_ylim(-70.1, 70.1)
        self.axes.set_xlim(0, 40)
        del self.xdata[:]
        del self.ydata[:]
        return self.lines

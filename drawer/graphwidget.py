from __future__ import print_function

import sys

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backends import qt4_compat
use_pyside = qt4_compat.QT_API == qt4_compat.QT_API_PYSIDE

import matplotlib.animation as animation
import math

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

    def create_main_frame(self):
        mainLayout = QHBoxLayout()
        self.main_frame = QWidget()

        self.fig = Figure((5.0, 4.0), dpi=100)
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
        t, y = data
        self.xdata.append(t)
        self.ydata.append(y)
        xmin, xmax = self.axes.get_xlim()
        ymin, ymax = self.axes.get_ylim()
        #self.lines = []
        if t >= xmax:
            self.axes.set_xlim(xmin, 2*xmax)
            self.axes.figure.canvas.draw()
        if y[0] >= ymax:
            self.axes.set_ylim(xmin, 2*ymax)
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
        return self.lines

    def on_draw(self):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)

        self.lines = []
        self.xdata, self.ydata = [], []

        #self.axes.plot(self.x, self.y, 'ro')
        #self.axes.imshow(self.data, interpolation='nearest')
        #self.axes.plot([1,2,3])
        self.ani = animation.FuncAnimation(self.fig, self.run, self.data_gen, blit=False, interval=10, repeat=False, init_func=self.init)
        self.canvas.draw()

    def data_gen(self, t=0):
        while self.nrn.get_time() < self.time_limit:
            sub_sec = None
            result = []
            for k, n in self.nrn.neurons.iteritems():
                sub_sec = n.get_selected_section()
                if sub_sec != None:
                    result.append(sub_sec.get_param('v')[0])
            if len(result) != 0:
                yield self.nrn.get_time(), result
            else:
                yield 0, [-40.0]

    def on_key_press(self, event):
        print('you pressed', event.key)
        # implement the default mpl key press events described at
        # http://matplotlib.org/users/navigation_toolbar.html#navigation-keyboard-shortcuts
        key_press_handler(event, self.canvas, self.mpl_toolbar)

    def init(self):
        self.axes.set_ylim(-50.1, 20.1)
        self.axes.set_xlim(0, 40)
        del self.xdata[:]
        del self.ydata[:]
        line, = self.axes.plot([], [], lw=2)
        line.set_data(self.xdata, self.ydata)
        self.lines.append(line)
        return self.lines
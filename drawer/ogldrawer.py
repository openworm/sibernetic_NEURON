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
from __future__ import with_statement

from PyQt4 import QtCore, QtGui
import os
import sys
from nsoglwidget import NSWidget
from graphwidget import NSGraphWidget

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from neuron import h


try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

__author__ = 'Sergey Khayrulin'

global nrn

nrn = None

class NSWindow(QtGui.QMainWindow):
    def __init__(self):
        super(NSWindow, self).__init__()
        self.resize(1492, 989)
        self.graph_window = None
        self.glWidget = NSWidget(nrn, self)
        self.glWidget.neuronSelectionChanged.connect(self.neuronsListSelectByName)
        self.setCentralWidget(self.glWidget)
        self.glWidget.show()
        self.xSlider = self.create_slider()
        #main_layout = QHBoxLayout()
        #main_layout.addWidget(self.glWidget)
        self.xSlider.setValue(15 * 16)

        self.create_menu()
        self.create_dock_window()
        self.create_toolbar()
        self.statusBar().setVisible(True)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.print_time)
        self.timer.start(0)

        #self.neurons_names()

    def create_menu(self):
        exit = QtGui.QAction(self)
        exit.setText(_translate("MainWindow", "Exit", None))
        exit.setShortcut('Ctrl+Q')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        zoom_plus_action = QtGui.QAction(self)
        zoom_plus_action.setText(_translate("MainWindow", "Zoom +", None))
        self.connect(zoom_plus_action, QtCore.SIGNAL('triggered()'), self.glWidget.zoom_plus)

        zoom_minus_action = QtGui.QAction(self)
        zoom_minus_action.setText(_translate("MainWindow", "Zoom -", None))
        self.connect(zoom_minus_action, QtCore.SIGNAL('triggered()'), self.glWidget.zoom_minus)

        neurons_list_action = QtGui.QAction(self)
        neurons_list_action.setText(_translate("MainWindow", "Show list of Neurons", None))
        self.connect(neurons_list_action, QtCore.SIGNAL('triggered()'), self.create_dock_window)

        load_model_action = QtGui.QAction(self)
        load_model_action.setText(_translate("MainWindow", "Load Model ...", None))
        self.connect(load_model_action, QtCore.SIGNAL('triggered()'), self.open_file_dialog)

        draw_graph_action = QtGui.QAction(self)
        draw_graph_action.setText(_translate("MainWindow", "Draw Graph ...", None))
        self.connect(draw_graph_action, QtCore.SIGNAL('triggered()'), self.draw_graph)

        about_action = QtGui.QAction(self)
        about_action.setText(_translate("MainWindow", "About", None))
        self.connect(about_action, QtCore.SIGNAL('triggered()'), self.actionAbout)

        menu_bar = self.menuBar()
        menu_file = menu_bar.addMenu("&File")
        menu_view = menu_bar.addMenu("&View")
        self.tools = menu_bar.addMenu("&Tools")
        menu_help = menu_bar.addMenu("&Help")

        menu_file.addAction(load_model_action)
        menu_file.addAction(exit)
        menu_view.addAction(zoom_plus_action)
        menu_view.addAction(zoom_minus_action)
        self.tools.addAction(draw_graph_action)
        menu_help.addAction(about_action)

    def create_slider(self):
        slider = QtGui.QSlider(QtCore.Qt.Vertical)
        slider.setRange(0, 360 * 16)
        slider.setSingleStep(16)
        slider.setPageStep(15 * 16)
        slider.setTickInterval(15 * 16)
        slider.setTickPosition(QSlider.TicksRight)
        return slider

    def neurons_names(self):
        l = 1
        for z in nrn.neurons_names: #self.glWidget.nrn.neurons:
            label = QtGui.QLabel(z, self.glWidget)
            label.setAutoFillBackground(False)
            label.setStyleSheet("background-color: rgba(128, 128, 128, 255)")
            label.move(50, l)
            l+=20

    def create_toolbar(self):
        self.myToolbar = QtGui.QToolBar("ToolBar")
        self.addToolBar(Qt.BottomToolBarArea, self.myToolbar)

        left_spacer = QtGui.QWidget()
        left_spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        right_spacer = QtGui.QWidget()
        right_spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.myToolbar.addWidget(left_spacer)

        pause_action = QtGui.QAction(QtGui.QIcon('drawer/icons/pause.png'), "Pause simulation", self)
        self.connect(pause_action, QtCore.SIGNAL('triggered()'), self.action_Pause)

        stop_action = QtGui.QAction(QtGui.QIcon('drawer/icons/stop.png'), "Stop simulation", self)
        self.connect(stop_action, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        remove_action = QtGui.QAction(QtGui.QIcon('drawer/icons/undo.png'), "Remove all selections", self)
        self.connect(remove_action, QtCore.SIGNAL('triggered()'), self.action_Remove_selection)

        zoom_in = QtGui.QAction(QtGui.QIcon('drawer/icons/zoom-in.png'), "Zoom the model in", self)
        self.connect(zoom_in, QtCore.SIGNAL('triggered()'), self.glWidget.zoom_plus)

        zoom_out = QtGui.QAction(QtGui.QIcon('drawer/icons/zoom-out.png'), "Zoom the model out", self)
        self.connect(zoom_out, QtCore.SIGNAL('triggered()'), self.glWidget.zoom_minus)

        self.myToolbar.addSeparator()
        self.myToolbar.addAction(zoom_out)
        self.myToolbar.addSeparator()
        self.myToolbar.addAction(zoom_in)
        self.myToolbar.addSeparator()
        self.myToolbar.addAction(pause_action)
        self.myToolbar.addSeparator()
        self.myToolbar.addAction(remove_action)
        self.myToolbar.addSeparator()
        self.myToolbar.addAction(stop_action)
        self.myToolbar.addSeparator()

        self.myToolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        self.myToolbar.addWidget(right_spacer)
        self.tools.addAction(self.myToolbar.toggleViewAction())

    def action_Pause(self):
        #self.myToolbar.setStyleSheet("self.pause_action.QToolButton {background-color: rgba(128, 128, 130, 255)}")
        self.glWidget.actionPause()

    def action_Remove_selection(self):
        for p, n in nrn.neurons.iteritems():
            if n.selected:
                n.turn_off_selection()
                self.neuronsListSelectByName(p, False)

    def print_time(self):
        time = "%.3f" % nrn.get_time()
        self.statusBar().showMessage("Current time of simulation:        " + str(time))

    def draw_graph(self):
        if self.graph_window is None:
            self.graph_window = NSGraphWidget(nrn, 400)
        self.graph_window.show()

    def open_file_dialog(self):
        """
        Opens a file dialog when "Load Model" has been triggered
        """
        global nrn

        self.glWidget.look_draw()
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File', os.getcwd(), ("Hoc files (*.hoc)"))
        if fileName:
            load_model(fileName)
            self.glWidget.update_scene(nrn)
        self.glWidget.look_draw()

    def open_input_dialog(self):
        """
        Opens input dialog to find the name of neuron
        """
        text, result = QtGui.QInputDialog.getText(self, " ", "Enter the neuron's name")

    def actionAbout(self):
        QtGui.QMessageBox.about(self, "About NEURON<->Python work environment",
                                "Sibernetic-NEURON using python-NEURON interface "
                                "for interraction with NEURON simulator. Script is "
                                "using model from *.hoc file (stored in model folder) "
                                "which is loading into NEURON and then run. OpenGL is "
                                "used for drawing results of simulation on the screen "
                                "on scene. Results are represented as 3D model showing "
                                "model you can rotate or scale it. The red color of "
                                "segment indicates changes of voltage in this segment. "
                                "Brightness depends on value of voltage in the current "
                                "moment.")

    def create_dock_window(self):
        dock = QtGui.QDockWidget("List of Neurons", self)
        dock.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        MyTreeWidget = QtGui.QTreeWidget(self)
        self.neuronsList = MyTreeWidget
        self.neuronsList.setHeaderHidden(True)
        self.neuronsList.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)

        for k, n in nrn.neurons.iteritems():
            self.neurons_names = QtGui.QTreeWidgetItem(self.neuronsList, [k])
            for sec, val in n.sections.iteritems():
                self.section = QtGui.QTreeWidgetItem(self.neurons_names, [sec])

        dock.setWidget(self.neuronsList)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        self.tools.addAction(dock.toggleViewAction())
        self.neuronsList.setMaximumWidth(200)

        self.neuronsList.itemClicked.connect(self.neuronsList_clicked)

    def neuronsList_clicked(self, item, m):
        if str(item.text(m)).find('_') != -1:
            item.setSelected(False)
            #for name, val in nrn.neurons.iteritems():
            #    if str(item.text(m)).startswith(name):
            #        s = val.sections[str(item.text(m))]
            #        if val.selected:
            #            if s.selected:
            #                s.selected = False
            #        else:
            #            val.selected = True
            #            s.selected = True
        else:
            print item.text(m)
            n = nrn.neurons[str(item.text(m))]
            if n.selected:
                n.turn_off_selection()
            else:
                n.selected = not n.selected


    def neuronsListSelectByName(self, name, isSelect = True, m=1):
        item = self.neuronsList.findItems(name, Qt.MatchExactly | Qt.MatchRecursive)[0] #.count()
        print (name, item, isSelect)
        item.setSelected(isSelect)


def load_model(model_filename='./model/_ria.hoc', tstop=400):
    """
    Load and initialize model from file
    on first step it run nrnivmodl in folder with model and gap.mod file to generate all
    binary libs and eeded files for work with NEURON
    :param model_filename: name of file with path to it
    :param tstop: time of duration of simulation
    """
    global nrn
    if nrn != None:
        nrn.finish()
    path, filename = os.path.split(str(model_filename))
    old_dir = os.path.abspath(os.getcwd())
    os.chdir(path)
    osplatform = sys.platform
    if osplatform.find('linux') != -1 or osplatform.find('darwin') != -1:
        os.system('nrnivmodl')
    elif osplatform.find('win'):
        pass
    print 'Current work directory is ' + os.getcwd()
    from NeuronWrapper import NrnSimulator
    nrn = NrnSimulator(filename, tstop=tstop)
    os.chdir(old_dir)


def run_window():
    """
    Run main Qt window (sudo apt-get install python-qt4ow)
    """
    load_model() #(model_filename='./model/avm.hoc')
    #load_model(model_filename='./model/pyramid.nrn')
    app = QApplication(["Neuron<->Python interactive work environment"])
    window = NSWindow()
    window.show()
    app.exec_()


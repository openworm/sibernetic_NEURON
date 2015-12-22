from PyQt4 import QtCore, QtGui
import os
import sys
from nsoglwidget import NSWidget

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

# coding=utf-8
__author__ = 'Sergey Khayrulin'

global nrn


class NSWindow(QtGui.QWidget):
    def __init__(self):
        super(NSWindow, self).__init__()
        self.resize(1492, 989)

        self.glWidget = NSWidget(nrn)

        self.xSlider = self.createSlider()
        self.ySlider = self.createSlider()
        self.zSlider = self.createSlider()
        self.treeView = QtGui.QTreeView()


        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        #mainLayout.addWidget(self.xSlider)
        #mainLayout.addWidget(self.ySlider)
        #mainLayout.addWidget(self.zSlider)
        #mainLayout.addWidget(self.treeView)

        self.xSlider.setValue(15 * 16)
        self.ySlider.setValue(345 * 16)
        self.zSlider.setValue(0 * 16)

        menubar = QtGui.QMenuBar()
        menubar.setGeometry(QtCore.QRect(0, 0, 1492, 25))
        menubar.setObjectName(_fromUtf8("menubar"))
        menuFile = QtGui.QMenu(menubar)
        menuFile.setObjectName(_fromUtf8("menuFile"))
        menuTools = QtGui.QMenu(menubar)
        menuTools.setObjectName(_fromUtf8("menuTools"))
        menuHelp = QtGui.QMenu(menubar)
        menuHelp.setObjectName(_fromUtf8("menuHelp"))
        actionLoad_Model = QtGui.QAction(self)
        actionLoad_Model.setObjectName(_fromUtf8("actionLoad_Model"))
        actionGraph_Widget = QtGui.QAction(self)
        actionGraph_Widget.setObjectName(_fromUtf8("actionGraph_Widget"))
        actionAbout = QtGui.QAction(self)
        actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionExit = QtGui.QAction(self)
        self.actionExit.setShortcut('Ctrl+Q')
        self.connect(self.actionExit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        menuFile.addAction(actionLoad_Model)
        menuFile.addAction(self.actionExit)
        menuTools.addAction(actionGraph_Widget)
        menuHelp.addAction(actionAbout)
        menubar.addAction(menuFile.menuAction())
        menubar.addAction(menuTools.menuAction())
        menubar.addAction(menuHelp.menuAction())

        menuFile.setTitle(_translate("MainWindow", "File", None))
        menuTools.setTitle(_translate("MainWindow", "Tools", None))
        menuHelp.setTitle(_translate("MainWindow", "Help", None))
        actionLoad_Model.setText(_translate("MainWindow", "Load Model", None))
        actionGraph_Widget.setText(_translate("MainWindow", "Graph Widget", None))
        actionAbout.setText(_translate("MainWindow", "About", None))
        self.actionExit.setText(_translate("MainWindow", "Exit", None))

        mainLayout.setMenuBar(menubar)

        self.setLayout(mainLayout)

        self.setWindowTitle("Python NEURON work environment")

    def createSlider(self):
        slider = QtGui.QSlider(QtCore.Qt.Vertical)
        slider.setRange(0, 360 * 16)
        slider.setSingleStep(16)
        slider.setPageStep(15 * 16)
        slider.setTickInterval(15 * 16)
        slider.setTickPosition(QtGui.QSlider.TicksRight)

        return slider


def load_model(model_filename='./model/avm.hoc', tstop=400):
    """
    Load and initialize model from file
    on first step it run nrnivmodl in folder with model and gap.mod file to generate all
    binary libs and eeded files for work with NEURON
    :param model_filename: name of file with path to it
    :param tstop: time of duration of simulation
    """
    global nrn
    path, filename = os.path.split(model_filename)
    os.chdir(path)
    osplatform = sys.platform
    if osplatform.find('linux') != -1 or osplatform.find('darwin') != -1:
        os.system('nrnivmodl')
    elif osplatform.find('win'):
        pass
    print 'Current work directory is ' + os.getcwd()
    from NeuronWrapper import NrnSimulator
    nrn = NrnSimulator(filename, tstop=400)


def run_window():
    """
    Run main Qt window
    """
    #load_model(model_filename='./model/_ria.hoc')
    load_model()
    app = QtGui.QApplication(["Neuron<->Python interactive work environment"])
    window = NSWindow()
    window.show()
    app.exec_()


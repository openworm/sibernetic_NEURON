from PyQt4 import QtCore, QtGui
import os
import sys
from nsoglwidget import NSWidget
from graphwidget import NSGraphWidget

from PyQt4.QtGui import *
from PyQt4.QtCore import *


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

# coding=utf-8
__author__ = 'Sergey Khayrulin'

global nrn


class NSWindow(QWidget):
    def __init__(self):
        super(NSWindow, self).__init__()
        self.resize(1492, 989)

        self.graph_window = None

        self.glWidget = NSWidget(nrn)

        self.xSlider = self.createSlider()
        self.ySlider = self.createSlider()
        self.zSlider = self.createSlider()
        self.treeView = QTreeView()


        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        #mainLayout.addWidget(self.xSlider)
        #mainLayout.addWidget(self.ySlider)
        #mainLayout.addWidget(self.zSlider)
        #mainLayout.addWidget(self.treeView)

        self.xSlider.setValue(15 * 16)
        self.ySlider.setValue(345 * 16)
        self.zSlider.setValue(0 * 16)

        menubar = QMenuBar()
        menubar.setGeometry(QRect(0, 0, 1492, 25))
        menubar.setObjectName(_fromUtf8("menubar"))
        menuFile = QMenu(menubar)
        menuFile.setObjectName(_fromUtf8("menuFile"))
        menuTools = QMenu(menubar)
        menuTools.setObjectName(_fromUtf8("menuTools"))
        menuHelp = QMenu(menubar)
        menuHelp.setObjectName(_fromUtf8("menuHelp"))
        self.actionAbout = QAction(self)
        self.actionExit = QAction(self)
        self.actionGraph = QAction(self)
        self.actionLoad_Model = QtGui.QAction(self)
        actionGraph_Widget = QtGui.QAction(self)
        actionGraph_Widget.setObjectName(_fromUtf8("actionGraph_Widget"))
        actionAbout = QtGui.QAction(self)
        actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionExit = QtGui.QAction(self)
        self.actionExit.setShortcut('Ctrl+Q')
        self.connect(self.actionExit, SIGNAL('triggered()'), SLOT('close()'))
        self.connect(self.actionAbout, SIGNAL('triggered()'), SLOT('about()'))
        self.connect(self.actionGraph, SIGNAL('triggered()'), SLOT('draw_graph()'))
        self.connect(self.actionLoad_Model, QtCore.SIGNAL('triggered()'), self.openFileDialog)
        self.actionLoad_Model.setObjectName(_fromUtf8("actionLoad_Model"))
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionGraph.setObjectName(_fromUtf8("actionGraph"))
        menuFile.addAction(self.actionLoad_Model)
        menuFile.addAction(self.actionExit)
        menuTools.addAction(self.actionGraph)
        menuHelp.addAction(self.actionAbout)
        menubar.addAction(menuFile.menuAction())
        menubar.addAction(menuTools.menuAction())
        menubar.addAction(menuHelp.menuAction())

        menuFile.setTitle(_translate("MainWindow", "File", None))
        menuTools.setTitle(_translate("MainWindow", "Tools", None))
        menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))
        self.actionLoad_Model.setText(_translate("MainWindow", "Load Model", None))
        actionGraph_Widget.setText(_translate("MainWindow", "Graph Widget", None))
        actionAbout.setText(_translate("MainWindow", "About", None))
        self.actionExit.setText(_translate("MainWindow", "Exit", None))
        self.actionGraph.setText(_translate("MainWindow", "Draw Graph", None))
        mainLayout.setMenuBar(menubar)

        self.setLayout(mainLayout)

        self.setWindowTitle("Python NEURON work environment")

    def createSlider(self):
        slider = QSlider(Qt.Vertical)
        slider.setRange(0, 360 * 16)
        slider.setSingleStep(16)
        slider.setPageStep(15 * 16)
        slider.setTickInterval(15 * 16)
        slider.setTickPosition(QSlider.TicksRight)

        return slider

    @pyqtSlot()
    def about(self):
        QMessageBox.about(self, "About", "This is an about box \n shown with QAction of QMenu.")

    @pyqtSlot()
    def draw_graph(self):
        if self.graph_window is None:
            self.graph_window = NSGraphWidget(nrn, 400)
        self.graph_window.show()

    def openFileDialog(self):
        """
        Opens a file dialog when "Load Model" has been triggered
        """
        #dialog = QtGui.QFileDialog(self)
        #QtGui.QFileDialog.setViewMode(list)
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '/home/nya/git/Sibernetic-NEURON', ("Hoc files (*.hoc)"))

        if fileName:
            #model_fileName = fileName
            #model_path = QFileInfo.absoluteFilePath(filePath)
            #model_path = QtGui.QFileDialog.directory(self)

            load_model(fileName)
            #window = NSWindow()
            #window.show()
            #self.label.setText(filename)


def load_model(model_filename='./model/_ria.hoc', tstop=400):
    """
    Load and initialize model from file
    on first step it run nrnivmodl in folder with model and gap.mod file to generate all
    binary libs and eeded files for work with NEURON
    :param model_filename: name of file with path to it
    :param tstop: time of duration of simulation
    """
    global nrn
    path, filename = os.path.split(str(model_filename))
    os.chdir(path)
    osplatform = sys.platform
    if osplatform.find('linux') != -1 or osplatform.find('darwin') != -1:
        os.system('nrnivmodl')
    elif osplatform.find('win'):
        pass
    print 'Current work directory is ' + os.getcwd()
    from NeuronWrapper import NrnSimulator
    nrn = NrnSimulator(filename, tstop=tstop)


def run_window():
    """
    Run main Qt windsudo apt-get install python-qt4ow
    """
    load_model(model_filename='./model/avm.hoc')
    #load_model()
    app = QApplication(["Neuron<->Python interactive work environment"])
    window = NSWindow()
    window.show()
    app.exec_()


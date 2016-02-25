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

nrn = None

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
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.glWidget)
        #main_layout.addWidget(self.xSlider)
        #main_layout.addWidget(self.ySlider)
        #main_layout.addWidget(self.zSlider)
        #main_layout.addWidget(self.treeView)

        self.xSlider.setValue(15 * 16)
        self.ySlider.setValue(345 * 16)
        self.zSlider.setValue(0 * 16)

        menu_bar = QMenuBar()
        menu_bar.setGeometry(QRect(0, 0, 1492, 25))
        menu_bar.setObjectName(_fromUtf8("menu_bar"))
        menu_file = QMenu(menu_bar)
        menu_file.setObjectName(_fromUtf8("menu_file"))
        menu_tools = QMenu(menu_bar)
        menu_tools.setObjectName(_fromUtf8("menu_tools"))
        menu_help = QMenu(menu_bar)
        menu_help.setObjectName(_fromUtf8("menu_help"))
        self.actionAbout = QAction(self)
        self.actionExit = QAction(self)
        self.actionGraph = QAction(self)
        self.actionLoad_Model = QtGui.QAction(self)
        action_graph_widget = QtGui.QAction(self)
        action_graph_widget.setObjectName(_fromUtf8("action_graph_widget"))
        action_about = QtGui.QAction(self)
        action_about.setObjectName(_fromUtf8("action_about"))
        self.actionExit = QtGui.QAction(self)
        self.actionExit.setShortcut('Ctrl+Q')
        self.connect(self.actionExit, SIGNAL('triggered()'), SLOT('close()'))
        self.connect(self.actionAbout, SIGNAL('triggered()'), SLOT('about()'))
        self.connect(self.actionGraph, SIGNAL('triggered()'), SLOT('draw_graph()'))
        self.connect(self.actionLoad_Model, QtCore.SIGNAL('triggered()'), self.open_file_dialog)
        self.actionLoad_Model.setObjectName(_fromUtf8("actionLoad_Model"))
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionAbout.setObjectName(_fromUtf8("action_about"))
        self.actionGraph.setObjectName(_fromUtf8("actionGraph"))
        menu_file.addAction(self.actionLoad_Model)
        menu_file.addAction(self.actionExit)
        menu_tools.addAction(self.actionGraph)
        menu_help.addAction(self.actionAbout)
        menu_bar.addAction(menu_file.menuAction())
        menu_bar.addAction(menu_tools.menuAction())
        menu_bar.addAction(menu_help.menuAction())

        menu_file.setTitle(_translate("MainWindow", "File", None))
        menu_tools.setTitle(_translate("MainWindow", "Tools", None))
        menu_help.setTitle(_translate("MainWindow", "Help", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))
        self.actionLoad_Model.setText(_translate("MainWindow", "Load Model", None))
        action_graph_widget.setText(_translate("MainWindow", "Graph Widget", None))
        action_about.setText(_translate("MainWindow", "About", None))
        self.actionExit.setText(_translate("MainWindow", "Exit", None))
        self.actionGraph.setText(_translate("MainWindow", "Draw Graph", None))
        main_layout.setMenuBar(menu_bar)

        self.setLayout(main_layout)

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

    def open_file_dialog(self):
        """
        Opens a file dialog when "Load Model" has been triggered
        """
        global nrn
        #dialog = QtGui.QFileDialog(self)
        #QtGui.QFileDialog.setViewMode(list)
        self.glWidget.look_draw()
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File', os.getcwd(), ("Hoc files (*.hoc)"))
        if fileName:
            #model_fileName = fileName
            #model_path = QFileInfo.absoluteFilePath(filePath)
            #model_path = QtGui.QFileDialog.directory(self)

            load_model(fileName)
            #window = NSWindow()
            #window.show()
            #self.label.setText(filename)
            self.glWidget.update_scene(nrn)
        self.glWidget.look_draw()


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
    load_model()#model_filename='./model/avm.hoc')
    #load_model()
    app = QApplication(["Neuron<->Python interactive work environment"])
    window = NSWindow()
    window.show()
    app.exec_()


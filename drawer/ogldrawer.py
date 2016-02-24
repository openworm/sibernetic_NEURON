from PyQt4 import QtCore, QtGui
import os
import sys
from nsoglwidget import NSWidget
from NeuronWrapper import NrnSimulator as NS
import numpy as np

#try:
#    _fromUtf8 = QtCore.QString.fromUtf8
#except AttributeError:
#    def _fromUtf8(s):
#        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

__author__ = 'Sergey Khayrulin'

global nrn

class NSWindow(QtGui.QMainWindow):
    def __init__(self):
        super(NSWindow, self).__init__()
        #QtGui.QMainWindow.__init__(self)
        self.resize(1492, 989)

        self.glWidget = NSWidget(nrn)
        self.setCentralWidget(self.glWidget)
        self.glWidget.show()

        self.xSlider = self.createSlider()
        #self.ySlider = self.createSlider()
        #self.zSlider = self.createSlider()
        self.treeView = QtGui.QTreeView()

        #layout = QtGui.QGridLayout(self.glWidget)
        #layout.addWidget(self.xSlider, 0, 0)

        #mainLayout.addWidget(self.zSlider)
        #mainLayout.addWidget(self.treeView)

        self.xSlider.setValue(15 * 16)
        #self.ySlider.setValue(345 * 16)
        #self.zSlider.setValue(0 * 16)

        self.exit = QtGui.QAction(self)
        self.exit.setText(_translate("MainWindow", "Exit", None))
        self.exit.setShortcut('Ctrl+Q')
        self.connect(self.exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        loadmodel = QtGui.QAction(self)
        loadmodel.setText(_translate("MainWindow", "Load Model ...", None))
        self.connect(loadmodel, QtCore.SIGNAL('triggered()'), self.openFileDialog)

        about = QtGui.QAction(self)
        about.setText(_translate("MainWindow", "About", None))
        self.connect(about, QtCore.SIGNAL('triggered()'), self.actionAbout)

        zoomPlus = QtGui.QAction(self)
        zoomPlus.setText(_translate("MainWindow", "Zoom +", None))
        self.connect(zoomPlus, QtCore.SIGNAL('triggered()'), self.glWidget.zoomPlus)

        zoomMinus = QtGui.QAction(self)
        zoomMinus.setText(_translate("MainWindow", "Zoom -", None))
        self.connect(zoomMinus, QtCore.SIGNAL('triggered()'), self.glWidget.zoomMinus)

        neuronsList = QtGui.QAction(self)
        neuronsList.setText(_translate("MainWindow", "Show list of Neurons", None))
        self.connect(neuronsList, QtCore.SIGNAL('triggered()'), self.createDockWindow)

        menubar = self.menuBar()
        file = menubar.addMenu("&File")
        view = menubar.addMenu("&View")
        self.tools = menubar.addMenu("&Tools")
        help = menubar.addMenu("&Help")

        file.addAction(loadmodel)
        file.addAction(self.exit)
        view.addAction(zoomPlus)
        view.addAction(zoomMinus)
        self.tools.addAction("Graph Widget")
        help.addAction(about)

        self.toolbar = self.addToolBar("ToolBar")
        self.toolbar.addAction("Play") #(self.exit)
        self.toolbar.addAction("Pause")
        self.toolbar.addAction("Stop")
        #self.toolbar.addAction(self.pause)

        self.createDockWindow()

        #self.neuronsNames()

        #self.setWindowTitle("Python NEURON work environment")

    def createSlider(self):
        slider = QtGui.QSlider(QtCore.Qt.Vertical)
        slider.setRange(0, 360 * 16)
        slider.setSingleStep(16)
        slider.setPageStep(15 * 16)
        slider.setTickInterval(15 * 16)
        slider.setTickPosition(QtGui.QSlider.TicksLeft)

        return slider

    def neuronsNames(self):
        l=1
        for z in nrn.neurons_names: #self.glWidget.nrn.neurons:
            label = QtGui.QLabel(z, self.glWidget)
            label.setAutoFillBackground(False)
            label.setStyleSheet("background-color: rgba(128, 128, 128, 255)")
            label.move(50,l)
            l+=20

    def openFileDialog(self):
        """
        Opens a file dialog when "Load Model" has been triggered
        """
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '/home/nya/git/Sibernetic-NEURON', ("Hoc files (*.hoc)"))

        if fileName:
            load_model(fileName)

    def openInputDialog(self):
        """
        Opens input dialog to find the name of neuron
        """
        text, result = QtGui.QInputDialog.getText(self, " ", "Enter the neuron's name")

    def actionAbout(self):
        QtGui.QMessageBox.about(self, "About NEURON<->Python work environment", "Here will be the information about this project...")

    def createDockWindow(self):
        dock = QtGui.QDockWidget("List of Neurons", self)
        dock.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self.neuronsList = QtGui.QListWidget(dock)
        for p in nrn.neurons_names:
            self.neuronsList.addItems([p])
        dock.setWidget(self.neuronsList)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        #self.neuronsList.setObjectName("Neurons")
        self.tools.addAction(dock.toggleViewAction())
        self.neuronsList.setMaximumWidth(100)

        #self.connect (self.neuronsList.currentTextChanged(), self.openInputDialog)

        #self.neuronsList.currentTextChanged.connect(lambda: self.selectingNeuron(self.neuronsList.currentItem))
        self.neuronsList.itemClicked.connect(lambda: self.selectingNeuron(self.neuronsList.currentItem))

    def selectingNeuron(self, name):
        for p in nrn.neurons_names:
            if p == name:
                self.glWidget.p.selected = not self.glWidget.p.selected


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


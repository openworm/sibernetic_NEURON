from PyQt4 import QtGui
import os
from window import NSWidget

# coding=utf-8
__author__ = 'Sergey Khayrulin'
global nrn


def load_model(modelfilename='./model/avm.hoc', tstop=400):
    """
    Load and initialize model from file
    on first step it run nrnivmodl in folder with model and gap.mod file to generate all
    binary libs and eeded files for work with NEURON
    :param modelfilename: name of file with path to it
    :param tstop: time of duration of simulation
    """
    global nrn
    outputfolder = 'x86_64' #TODO make it custom it depends on your platform if now
    workdir = os.getcwd()
    path, filename = os.path.split(modelfilename)
    os.chdir(path)
    os.system('nrnivmodl')
    #os.system('rsync -ar --remove-source-files ' + outputfolder + ' ' + workdir)
    #os.chdir(workdir)
    print 'Current work directory is ' + os.getcwd()
    from NeuronWrapper import NrnSimulator
    nrn = NrnSimulator(filename, tstop=400)


def run_window():
    """
    Run main Qt window
    """
    load_model()
    app = QtGui.QApplication(["Neuron<->Python interactive work environment"])
    widget = NSWidget(nrn)
    widget.show()
    app.exec_()


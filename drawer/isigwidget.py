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

from PyQt4.QtGui import *
import threading

class NSISigWidget(QWidget, threading.Thread):
    def __init__(self, nrn, parent=None):
        super(NSISigWidget, self).__init__(parent)
        self.resize(200, 300)

        self.nrn = nrn
        layout = QFormLayout()
        self.btn = QPushButton("Run")
        self.btn.clicked.connect(self.input_signal)
        self.amp = QLineEdit()
        self.delay = QLineEdit()
        self.duration = QLineEdit()
        layout.addRow(self.amp)
        layout.addRow(self.delay)
        layout.addRow(self.duration)
        layout.addRow(self.btn)
        self.setLayout(layout)
        self.setWindowTitle('Input signal into selected segment')

    def input_signal(self):
        self.nrn.add_stim(float(str(self.amp.text())),float(str(self.delay.text())), float(str(self.duration.text())))
        print 'Input signal into neuson'
        self.close()
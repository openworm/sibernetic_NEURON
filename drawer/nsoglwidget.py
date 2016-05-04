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

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
from PyQt4.QtCore import *
from PyQt4.QtOpenGL import *

import math
import numpy as np
from math import sqrt, pi, acos


class NSWidget(QGLWidget):

    neuronSelectionChanged = pyqtSignal(unicode, bool)

    def __init__(self, nrn, NSWindow):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH | GLUT_STENCIL)
        super(NSWidget, self).__init__()
        self.setMouseTracking(True)
        self.__init_vars(nrn)
        self.look_draw_state = False
        self.ifPause = False
        self.parent = NSWindow

    def __init_vars(self, nrn):
        """
        Init all variables for drawing
        :param nrn:
        :return:
        """
        self.x_rot = 0.0
        self.y_rot = 0.0
        self.ambient = (1.0, 1.0, 1.0, 1)
        self.neuron_color = (0.1, 0.1, 0.1, 0.1)
        self.light_pos = (0.0, 0.0, 1.0)
        # init NEURON SIMULATOR
        self.nrn = nrn
        self.cameraTrans = [-0.4, 0.0, -2.0]
        self.cameraRot = [0] * 3
        self.cameraTransLag = [-0.4, 0.0, -2.0]
        self.cameraRotLag = [0] * 3
        self.model_view = [0] * 16
        self.scale = 0.01
        self.old_x = 0
        self.old_y = 0
        self.axis_x = np.array([1.0, 0.0, 0.0])
        self.axis_y = np.array([0.0, 1.0, 0.0])
        self.axis_z = np.array([0.0, 0.0, 1.0])
        #self.max_diam = 0
        #self.x_name = 0
        #self.y_name = 0

    def __cylinder_2p(self, s, dim):
        """
        adapted from http://www.thjsmith.com/40/cylinder-between-two-points-opengl-c
        Drawing cylinder by two points
        Algorithm:
        1) calculate vector between end and start of segment
        2) calculate angle between Axis OZ and this vector
        3) translate System of coordinates into start position
        4) rotate on angle
        5) draw cylinder
        """
        diam_scale = 1 / self.scale
        v1 = np.array([s.start_x * self.scale, s.start_y * self.scale, s.start_z * self.scale])
        v2 = np.array([s.end_x * self.scale, s.end_y * self.scale, s.end_z * self.scale])
        v2r = v2 - v1
        # the rotation axis is the cross product between Z and v2r
        ax = np.cross(self.axis_z, v2r)
        l = sqrt(np.dot(v2r, v2r))
        if sqrt(np.dot(ax, ax)) == 0:
            ax = np.array([1.0, 0.0, 0.0])
        # get the angle using a dot product
        angle = 180.0 / pi * acos(np.dot(self.axis_z, v2r) / l)

        glPushMatrix()
        glTranslatef(v1[0], v1[1], v1[2])
        if angle == 180.0:
            angle = -angle
        glRotatef(angle, ax[0], ax[1], ax[2])
        glutSolidCylinder(s.diam / diam_scale, l, dim, dim)
        glPopMatrix()

    def paintGL(self):
        """
        Display function draws scene
        """
        glClearStencil(0)
        glClear(GL_COLOR_BUFFER_BIT| GL_DEPTH_BUFFER_BIT| GL_STENCIL_BUFFER_BIT)

        neurons = self.nrn.neurons

        # Draw all neurons
        for k, n in neurons.iteritems():
            if n.selected:
                self.neuron_color = (0.0, 0.5, 0.5, 0.1) #(0.1, 0.8, 0.0, 0.1) (0.0, 1.0, 1.0, 0.3) #(0.0, 0.5, 0.5, 0.1)
            else:
                self.neuron_color = (0.1, 0.1, 0.1, 0.1)
            for sec in n.sections.values():
                for sub_sec in sec.sub_sections:
                    #if self.max_diam < sub_sec.diam:
                    #    max_diam = sub_sec.diam
                    #    self.x_name = sub_sec.start_x
                    #    self.y_name = sub_sec.start_y
                    sub_section_color = self.neuron_color
                    vol = math.fabs(sub_sec.get_param('v')[0])
                    #    print sub_sec.get_param('v')[0]
                    if sub_sec.get_param('v')[0] > -40.0:
                        sub_section_color = (1 * 0.02 *(sub_sec.get_param('v')[0] + 40), 0.0, 0.0, 0.1)
                    elif sub_sec.selected:
                        sub_section_color = (0.7, 0.6, 0.0, 0.1)
                    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, sub_section_color)
                    glStencilFunc(GL_ALWAYS, sub_sec.index + 1, -1)
                    self.__cylinder_2p(sub_sec, 20)

            #glWindowPos2f(self.x_name * 2.65 + 550, self.y_name * 2.65 + 320)
            #glColor(0.5, 1.0, 0.0, 1.0)
            #glutBitmapString(GLUT_BITMAP_HELVETICA_12, k)

        glFlush()


    def resizeGL(self, width, height):
        """
        Run when we reshape window
        :param width: current width of window
        :param height: current height of window
        """
        if height == 0:
            height = 1
        if width == 0:
            width = 1

        glViewport(0, 0, width, height)
        glOrtho(0, width, 0, height, -1, 1)

        self.aspect = float(width) / float(height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(55.0, self.aspect, 0.1, 100.0)

        glClear(GL_COLOR_BUFFER_BIT| GL_DEPTH_BUFFER_BIT| GL_STENCIL_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        #for c in range(3):
        #    self.cameraTransLag[c] += self.cameraTrans[c] - self.cameraTransLag[c]
        #    self.cameraRotLag[c] += self.cameraRot[c] - self.cameraRotLag[c]
        #    #print self.cameraRotLag[c]
        #glTranslatef(self.cameraTransLag[0], self.cameraTransLag[1], self.cameraTransLag[2])
        #glRotatef(self.cameraRotLag[0], 1.0, 0.0, 0.0)
        #glRotatef(self.cameraRotLag[1], 0.0, 1.0, 0.0)
        #self.model_view = glGetFloatv(GL_MODELVIEW_MATRIX)

    def __update_data(self):
        if self.look_draw_state:
            return
        self.updateGL()
        if self.ifPause == True:
            return
        self.nrn.one_step()

    def initializeGL(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.__update_data)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_pos)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.5, 0.5, 0.5, 1.0)

        glEnable(GL_STENCIL_TEST)
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)

        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        self.timer.start(0)

    def mouseMoveEvent(self, mouseEvent):
        """
        Work when mouse is moved
        :param x: current coordinate of mouse pointer
        :param y: current coordinate of mouse pointer
        """
        x = mouseEvent.x()
        y = mouseEvent.y()
        dx = float(x - self.old_x)
        dy = float(y - self.old_y)

        if int(mouseEvent.buttons()) == Qt.LeftButton:
            self.cameraRot[0] += dy / 5.0
            self.cameraRot[1] += dx / 5.0
        if int(mouseEvent.buttons()) == Qt.RightButton:
            self.cameraTrans[0] += dx / 500.0
            self.cameraTrans[1] -= dy / 500.0
        if int(mouseEvent.buttons()) == Qt.MiddleButton:
            self.cameraTrans[2] += (dy / 500.0) * 0.5 * math.fabs(self.cameraTrans[2])
        self.old_x = x
        self.old_y = y
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        for c in range(3):
            self.cameraTransLag[c] += self.cameraTrans[c] - self.cameraTransLag[c]
            self.cameraRotLag[c] += self.cameraRot[c] - self.cameraRotLag[c]
        glTranslatef(self.cameraTransLag[0], self.cameraTransLag[1], self.cameraTransLag[2])
        glRotatef(self.cameraRotLag[0], 1.0, 0.0, 0.0)
        glRotatef(self.cameraRotLag[1], 0.0, 1.0, 0.0)
        self.model_view = glGetFloatv(GL_MODELVIEW_MATRIX)


    def mouseDoubleClickEvent(self, e): #mousePressEvent
        self.old_x = e.x()
        self.old_y = e.y()
        if int(e.buttons()) == Qt.LeftButton:
            index = glReadPixels(e.x(),  self.height() - e.y() - 1, 1, 1, GL_STENCIL_INDEX, GL_UNSIGNED_INT)
            if index[0][0] != 0:
                #print "selected object " + str(index[0][0] - 1)
                for k, n in self.nrn.neurons.iteritems():
                    for sec, val in n.sections.iteritems():
                        for sub_sec in val.sub_sections:
                            if index[0][0] - 1 == sub_sec.index:
                                if not sub_sec.selected:
                                    n.turn_off_selection()
                                    n.selected = True
                                    val.selected = True
                                    sub_sec.selected = True
                                    for sec1, val1 in n.sections.iteritems():
                                        if sec1 != sec:
                                            self.neuronSelectionChanged.emit(sec1, val1.selected)
                                else:
                                    n.turn_off_selection()
                        self.neuronSelectionChanged.emit(sec, val.selected)
                    self.neuronSelectionChanged.emit(k, n.selected)
            else:
                for k, n in self.nrn.neurons.iteritems():
                    n.turn_off_selection()
                    self.neuronSelectionChanged.emit(k, False)
                    for sec, val in n.sections.iteritems():
                        self.neuronSelectionChanged.emit(sec, val.selected)


    def wheelEvent(self, event):
        if event.delta() > 0:
            self.zoom_plus()
        else:
            self.zoom_minus()

    def look_draw(self):
        self.look_draw_state = not self.look_draw_state
        pass

    def update_scene(self, new_nrn):
        self.initializeGL()
        self.__init_vars(new_nrn)

    def system_of_coordinates(self):
        pass

    def zoom_plus(self):
        self.scale *= 1.1

    def zoom_minus(self):
        self.scale /=1.1

    def actionPause(self):
        self.ifPause = not self.ifPause
        #print self.ifPause


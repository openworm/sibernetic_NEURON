from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
from PyQt4.QtCore import *
from PyQt4.QtOpenGL import *

import math
import numpy as np
from math import sqrt, pi, acos


class NSWidget(QGLWidget):
    def __init__(self, nrn, parent=None):
        glutInit(sys.argv)
        self.xrot = 0.0
        self.yrot = 0.0
        self.ambient = (1.0, 1.0, 1.0, 1)
        self.treecolor = (0.1, 0.1, 0.1, 0.8) #TODO rename
        self.lightpos = (1.0, 1.0, -2.0)
        # init NEURON SIMULATOR
        self.nrn = nrn
        self.cameraTrans = [0, 0, -1.0]
        self.cameraRot = [0] * 3
        self.cameraTransLag = [0, 0, -1.0]
        self.cameraRotLag = [0] * 3
        self.modelView = [0] * 16
        self.scale = 0.01
        self.old_x = 0
        self.old_y = 0
        self.cameraTrans = [0, 0, -1.0]
        self.cameraRot = [0] * 3
        self.cameraTransLag = [0, 0, -1.0]
        self.cameraRotLag = [0] * 3
        self.modelView = [0] * 16
        self.scale = 0.01
        self.old_x = 0
        self.old_y = 0
        self.buttonState = Qt.NoButton
        super(NSWidget, self).__init__(parent)
        self.setMouseTracking(True)

    def __cylinder_2p(self, s, dim):
        """
        adapted from http://www.thjsmith.com/40/cylinder-between-two-points-opengl-c
        Drawing cylinder by two point
        Algorithm:
        1) calculate vector between end and start of section
        2) calculate angle between Axis OZ and this vector
        3) translate System of coordinates into start position
        4) rotate on angle
        5) draw cylinder
        """
        diamScale = 1 / self.scale
        v1 = np.array([s.start_x * self.scale, s.start_y * self.scale, s.start_z * self.scale])
        v2 = np.array([s.end_x * self.scale, s.end_y * self.scale, s.end_z * self.scale])
        v2r = v2 - v1
        z = np.array([0.0, 0.0, 1.0])
        # the rotation axis is the cross product between Z and v2r
        ax = np.cross(z, v2r)
        l = sqrt(np.dot(v2r, v2r))
        if sqrt(np.dot(ax, ax)) == 0:
            ax = np.array([1.0, 0.0, 0.0])
        # get the angle using a dot product
        angle = 180.0 / pi * acos(np.dot(z, v2r) / l)

        glPushMatrix()
        glTranslatef(v1[0], v1[1], v1[2])
        if angle == 180.0:
            angle = -angle
        glRotatef(angle, ax[0], ax[1], ax[2])
        glutSolidCylinder(s.diam / diamScale, l, dim, dim)
        glPopMatrix()

    def paintGL(self):
        """
        Display function draws scene
        """

        # Making one step of simulation
        neurons = self.nrn.neurons
        self.lightpos = (1.0 * self.scale, 1.0 * self.scale, -2.0 * self.scale)
        glClear(GL_COLOR_BUFFER_BIT)  # Clean screen
        glLightfv(GL_LIGHT0, GL_POSITION, self.lightpos)  # light is ratating with objects

        # Draw all neurons
        for k, n in neurons.iteritems():
            for sec in n.section:
                for sub_sec in sec.sub_sec:
                    self.treecolor = (0.1 * sub_sec.get_param('v'), 0.0 * sub_sec.get_param('v'), 0.0 * sub_sec.get_param('v'), 0.1)
                    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, self.treecolor)
                    self.__cylinder_2p(sub_sec, 20)
        #self.updateGL()
        #glutSwapBuffers()  # Show on screen

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
        glDepthRangef(-1.0, 1.0)
        '''
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspectRatio = float(width) / float(height);
        if aspectRatio > 1.0:
            glFrustum(-1*aspectRatio, 1*aspectRatio, -1, 1, 3, 45)
        else:
            glFrustum(-1, 1, -1/aspectRatio, 1/aspectRatio, 3, 45)
        '''
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        for c in range(3):
            self.cameraTransLag[c] += self.cameraTrans[c] - self.cameraTransLag[c]
            self.cameraRotLag[c] += self.cameraRot[c] - self.cameraRotLag[c]
        glTranslatef(self.cameraTransLag[0], self.cameraTransLag[1], self.cameraTransLag[2])
        glRotatef(self.cameraRotLag[0], 1.0, 0.0, 0.0)
        glRotatef(self.cameraRotLag[1], 0.0, 1.0, 0.0)
        modelView = glGetFloatv(GL_MODELVIEW_MATRIX)

    def __updatedata(self):
        self.nrn.one_step()
        self.updateGL()

    def initializeGL(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.__updatedata)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, self.lightpos)
        glClearColor(0.5, 0.5, 0.5, 1.0)
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
        modelView = glGetFloatv(GL_MODELVIEW_MATRIX)

    def mousePressEvent(self, e):
        self.old_x = e.x()
        self.old_y = e.y()

    def wheelEvent(self, event):
        if event.delta() > 0:
            self.scale *= 1.1
        else:
            self.scale /= 1.1

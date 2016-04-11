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
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH | GLUT_STENCIL)
        super(NSWidget, self).__init__(parent)
        self.setMouseTracking(True)
        self.__init_vars(nrn)
        self.look_draw_state = False

    def __init_vars(self, nrn):
        """
        Init all variables for drawing
        :param nrn:
        :return:
        """
        self.x_rot = 0.0
        self.y_rot = 0.0
        self.ambient = (1.0, 1.0, 1.0, 1)
        self.neuron_color = (0.1, 0.1, 0.1, 0.8)
        self.light_pos = (1.0, 1.0, -2.0)
        # init NEURON SIMULATOR
        self.nrn = nrn
        self.cameraTrans = [0, 0, -1.0]
        self.cameraRot = [0] * 3
        self.cameraTransLag = [0, 0, -1.0]
        self.cameraRotLag = [0] * 3
        self.model_view = [0] * 16
        self.scale = 0.01
        self.old_x = 0
        self.old_y = 0

    def __cylinder_2p(self, s, dim):
        """
        adapted from http://www.thjsmith.com/40/cylinder-between-two-points-opengl-c
        Drawing cylinder by two point
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
        glutSolidCylinder(s.diam / diam_scale, l, dim, dim)
        glPopMatrix()

    def paintGL(self):
        """
        Display function draws scene
        """
        glClearStencil(0)
        glClear(GL_COLOR_BUFFER_BIT| GL_DEPTH_BUFFER_BIT| GL_STENCIL_BUFFER_BIT)

        neurons = self.nrn.neurons
        self.light_pos = (1.0 * self.scale, 1.0 * self.scale, -2.0 * self.scale)
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_pos)  # light is ratating with objects
        glEnable(GL_STENCIL_TEST)
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
        # Draw all neurons
        for k, n in neurons.iteritems():
            if n.selected:
                self.neuron_color = (0.0, 0.5, 0.5, 0.1)
            else:
                self.neuron_color = (0.1, 0.1, 0.1, 0.1)
            for sec in n.sections:
                for sub_sec in sec.sub_sections:
                    sub_section_color = self.neuron_color
                    if sub_sec.selected:
                        sub_section_color = (0.7, 0.7, 0.0, 0.1)
                    #sub_segment_color = (sub_segment_color[0] * math.fabs(sub_sec.get_param('v')[0]), sub_segment_color[1] *
                    #                     math.fabs(sub_sec.get_param('v')[0]), sub_segment_color[2] * math.fabs(sub_sec.get_param('v')[0]),
                    #                     0.1)
                    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, sub_section_color)
                    glStencilFunc(GL_ALWAYS, sub_sec.index + 1, -1)
                    self.__cylinder_2p(sub_sec, 20)
        kl = 0

        for k, n in neurons.iteritems():
            kl += 20
            glWindowPos2i(100, 600-kl)
            glColor(0.5, 1.0, 0.0, 1.0)
            glutBitmapString(GLUT_BITMAP_HELVETICA_12, k)
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
        self.model_view = glGetFloatv(GL_MODELVIEW_MATRIX)

    def __update_data(self):
        if self.look_draw_state:
            return
        self.nrn.one_step()
        self.updateGL()

    def initializeGL(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.__update_data)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_pos)
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
        self.model_view = glGetFloatv(GL_MODELVIEW_MATRIX)

    def mousePressEvent(self, e):
        self.old_x = e.x()
        self.old_y = e.y()
        if int(e.buttons()) == Qt.LeftButton:
            index = glReadPixels(e.x(),  self.height() - e.y() - 1, 1, 1, GL_STENCIL_INDEX, GL_UNSIGNED_INT)
            if index[0][0] != 0:
                #print "selected object " + str(index[0][0] - 1)
                for k, n in self.nrn.neurons.iteritems():
                    for sec in n.sections:
                        for sub_sec in sec.sub_sections:
                            if index[0][0] - 1 == sub_sec.index:
                                if not n.selected:
                                    n.selected = True
                                    sub_sec.selected = n.selected
                                    sec.selected = n.selected
                                else:
                                    n.turn_off_selection()
                                return

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

    def zoom_plus(self):
        self.scale *= 1.1

    def zoom_minus(self):
        self.scale /=1.1


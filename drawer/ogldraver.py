# coding=utf-8
__author__ = 'serg'


from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *

from NeuronWrapper import NrnSimulator
import sys
import math


global xrot         # Величина вращения по оси x
global yrot         # Величина вращения по оси y
global ambient      # рассеянное освещение
global greencolor   # Цвет елочных иголок
global treecolor    # Цвет елочного стебля
global lightpos     # Положение источника освещения
global neurons      # List of Neurons
global scale
global old_x
global old_y
global buttonState
global cameraTrans
global cameraRot
global cameraTransLag
global cameraRotLag
global modelView
global winIdMain
global nrn

cameraTrans = [0, 0, -1.0]
cameraRot = [0]*3
cameraTransLag = [0, 0, -1.0]
cameraRotLag = [0]*3
modelView = [0]*16
scale = 0.01
old_x = 0
old_y = 0

def renderCylinder(s, subdivision, quadric):
    global scale
    diamScale = 1 / scale
    vx = (s.end_x - s.start_x) * scale
    vy = (s.end_y - s.start_y) * scale
    vz = (s.end_z - s.start_z) * scale

    if vz == 0:
       vz = 0.0001

    v = math.sqrt(vx*vx + vy*vy + vz*vz)
    ax = 57.2957795*math.acos(vz/v)
    if vz < 0:
        ax = -ax
    rx = -vy * vz
    ry = vx * vz
    glPushMatrix()

    glTranslatef(s.start_x*scale, s.start_y*scale, s.start_z*scale)
    glRotatef(ax, rx, ry, 0.0)
    gluQuadricOrientation(quadric, GLU_OUTSIDE)
    gluCylinder(quadric, s.diam/diamScale, s.diam/diamScale, v, subdivision, 1)
    #draw the first cap
    gluQuadricOrientation(quadric, GLU_INSIDE)
    gluDisk(quadric, 0.0, s.diam/diamScale, subdivision, 1)
    glTranslatef(0, 0, v)

    #draw the second cap
    gluQuadricOrientation(quadric, GLU_OUTSIDE)
    gluDisk(quadric, 0.0, s.diam/diamScale, subdivision, 1)
    glPopMatrix()


def renderCylinderConvinien(s, subdivision):
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    renderCylinder(s, subdivision, quadric)
    gluDeleteQuadric(quadric)


def display():
    global xrot
    global yrot
    global lightpos
    global greencolor
    global treecolor
    global neurons
    global scale
    global neurons
    global nrn

    # Making one step of simulation
    nrn.one_step()
    neurons = nrn.neurons
    ###########
    lightpos = (1.0 * scale, 1.0 * scale, -2.0 * scale)
    glClear(GL_COLOR_BUFFER_BIT)                                # Очищаем экран и заливаем серым цветом
    glLightfv(GL_LIGHT0, GL_POSITION, lightpos)                 # Источник света вращаем вместе с елкой

    # Рисуем ствол елки
    # Устанавливаем материал: рисовать с 2 сторон, рассеянное освещение, коричневый цвет
    for k, n in neurons.iteritems():
        for sec in n.section:
            for sub_sec in sec.sub_sec:
                treecolor = (0.1 * sub_sec.get_param('v'), 0.0 * sub_sec.get_param('v'), 0.0 * sub_sec.get_param('v'), 0.1)
                glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, treecolor)
                renderCylinderConvinien(sub_sec, 32)
    glutSwapBuffers()                                           # Выводим все нарисованное в памяти на экран


def reshape(width, height):
    global cameraTrans
    global cameraRot
    global cameraTransLag
    global cameraRotLag
    global scale
    if height == 0:
        height = 1
    if width == 0:
        width = 1

    glViewport(0, 0, width, height)
    glDepthRangef(-100.0, 100.0)
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
        cameraTransLag[c] += cameraTrans[c] - cameraTransLag[c]
        cameraRotLag[c] += cameraRot[c] - cameraRotLag[c]
    glTranslatef(cameraTransLag[0], cameraTransLag[1], cameraTransLag[2])
    glRotatef(cameraRotLag[0], 1.0, 0.0, 0.0)
    glRotatef(cameraRotLag[1], 0.0, 1.0, 0.0)
    glGetFloatv(GL_MODELVIEW_MATRIX, modelView)


def keyboard(key, x, y):
    global xrot
    global yrot
    # Обработчики для клавиш со стрелками
    if key == GLUT_KEY_UP:      # Клавиша вверх
        xrot -= 2.0             # Уменьшаем угол вращения по оси X
    if key == GLUT_KEY_DOWN:    # Клавиша вниз
        xrot += 2.0             # Увеличиваем угол вращения по оси X
    if key == GLUT_KEY_LEFT:    # Клавиша влево
        yrot -= 2.0             # Уменьшаем угол вращения по оси Y
    if key == GLUT_KEY_RIGHT:   # Клавиша вправо
        yrot += 2.0             # Увеличиваем угол вращения по оси Y

def init():
    global xrot         # Величина вращения по оси x
    global yrot         # Величина вращения по оси y
    global ambient      # Рассеянное освещение
    global greencolor   # Цвет елочных иголок
    global treecolor    # Цвет елочного ствола
    global lightpos     # Положение источника освещения
    global nrn

    xrot = 0.0                          # Величина вращения по оси x = 0
    yrot = 0.0                          # Величина вращения по оси y = 0
    ambient = (1.0, 1.0, 1.0, 1)        # Первые три числа - цвет в формате RGB, а последнее - яркость
    greencolor = (0.2, 0.8, 0.0, 0.8)   # Зеленый цвет для иголок
    treecolor = (0.1, 0.1, 0.1, 0.8)    # Коричневый цвет для ствола
    lightpos = (1.0, 1.0, -2.0)          # Положение источника освещения по осям xyz

    glClearColor(0.5, 0.5, 0.5, 1.0)                # Серый цвет для первоначальной закраски
    #gluOrtho2D(-4.0, 4.0, -4.0, 4.0)                # Определяем границы рисования по горизонтали и вертикали
    #glOrtho(-10.0, 10.0, -10.0, 10.0, -8.0, 8.0)                # Определяем границы рисования по горизонтали и вертикали
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient) # Определяем текущую модель освещения
    glEnable(GL_LIGHTING)                           # Включаем освещение
    glEnable(GL_LIGHT0)                             # Включаем один источник света
    glLightfv(GL_LIGHT0, GL_POSITION, lightpos)     # Определяем положение источника света

    # init NEURON SIMULATOR
    nrn = NrnSimulator('./model/avm.hoc', tstop=400)


def mouse(button, state, x, y):
    """

    :type state: object
    """
    global old_x
    global old_y
    global scale
    global buttonState
    if button == GLUT_LEFT_BUTTON:
        buttonState = 1
    if button == GLUT_RIGHT_BUTTON:
        buttonState = 3
    mods = glutGetModifiers()
    if mods & GLUT_ACTIVE_CTRL:
        buttonState = 2
    if state == GLUT_UP:
        buttonState = 0
    old_x = x
    old_y = y
    if button == 3:
        scale *= 1.1
    if button == 4:
        scale /= 1.1


def mouseMotion(x, y):
    """

    :param x:
    :param y:
    """

    global old_x
    global old_y
    global cameraTrans
    global cameraRot
    global cameraTransLag
    global cameraRotLag
    global buttonState

    dx = float(x - old_x)
    dy = float(y - old_y)

    if buttonState == 1:
        cameraRot[0] += dy / 5.0
        cameraRot[1] += dx / 5.0
    if buttonState == 3:
        cameraTrans[0] += dx / 500.0
        cameraTrans[1] -= dy / 500.0
    if buttonState == 2:
        cameraTrans[2] += (dy / 500.0) * 0.5 * math.fabs(cameraTrans[2])
    old_x = x
    old_y = y
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    for c in range(3):
        cameraTransLag[c] += cameraTrans[c] - cameraTransLag[c]
        cameraRotLag[c] += cameraRot[c] - cameraRotLag[c]
    glTranslatef(cameraTransLag[0], cameraTransLag[1], cameraTransLag[2])
    glRotatef(cameraRotLag[0], 1.0, 0.0, 0.0)
    glRotatef(cameraRotLag[1], 0.0, 1.0, 0.0)
    glGetFloatv(GL_MODELVIEW_MATRIX, modelView)


def timer(value):
    glutPostRedisplay()
    glutTimerFunc(0, timer, 0)


def run_window():
    global winIdMain
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
    winIdMain = glutCreateWindow('NEURON <-> Sibernetic')
    glutReshapeWindow(1024, 1024)
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutSpecialFunc(keyboard)
    glutMouseFunc(mouse)
    glutMotionFunc(mouseMotion)
    glutTimerFunc(0, timer, 0)
    init()
    glutMainLoop()
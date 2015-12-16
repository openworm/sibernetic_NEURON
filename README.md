# Sibernetic-NEURON

Main information
------------------------------
Sibernetic-NEURON using python-NEURON interface for interraction with NEURON simulator. Script is using model from *.hoc file (stored in model folder) which is loading into NEURON and than run. OpenGL is using for drawing result of simulation on the screen on scene. Reults is representing as 3D model showing model you can rotate or scaling it. Red color of segment indicates changes of voltage of in thsi segment. Brightnes depends on value of voltage in current moment.

Running (Linux/mac)
------------------------------
For runing main.py script you need prepare your enviroment before:

1. Install ipython documentation [here](http://ipython.org/install.html).
2. Install [NEURON with Python](http://www.davison.webfactional.com/notes/installation-neuron-python/)
3. Install OpenGL for python. For ubuntu you can run this ```sudo apt-get install python-opengl```
4. Install PyQt 4. For ubuntu you can run ```sudo apt-get install sudo apt-get install python-qt4```
4. Clone repository run this ```git clone https://github.com/openworm/Sibernetic-NEURON.git```
6. Than you can run application ```python main.py```


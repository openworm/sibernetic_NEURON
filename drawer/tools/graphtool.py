import matplotlib.pyplot as plt
from matplotlib.backend_bases import key_press_handler


class Graph:
    def __init__(self, nrn):
        self.nrn = nrn
        self.fig = plt.subplots()[0]
        self.on_draw()
        self.legend_list = []

    def run(self):#, data):
        plt.ion()
        # update the data
        data = self.data_gen()
        t, y, names = data
        self.xdata.append(t)
        self.ydata.append(y)
        xmin, xmax = self.axes.get_xlim()
        ymin, ymax = self.axes.get_ylim()
        # self.lines = []
        if t >= xmax:
            self.axes.set_xlim(xmin, 2 * xmax)
            self.axes.figure.canvas.draw()
        if y[0] >= ymax:
            self.axes.set_ylim(xmin, 2 * ymax)
            self.axes.figure.canvas.draw()
        for i in xrange(len(self.ydata[-1])):
            if i == len(self.ydata[-1]) - 1 and i + 1 < len(self.lines):
                self.lines.pop(i)
                break
            res = []
            for j in xrange(len(self.ydata)):
                if i < len(self.ydata[j]):
                    res.append(self.ydata[j][i])
            if i >= len(self.lines):
                line, = self.axes.plot([], [], lw=1)
                self.lines.append(line)
            self.lines[i].set_data(self.xdata[len(self.xdata) - len(res):], res)
        legend = self.axes.legend(self.lines, names, fancybox=True)
        for label in legend.get_texts():
            label.set_fontsize('small')
        self.fig.canvas.draw()
        return self.lines

    def on_draw(self):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        self.lines = []
        self.texts = []
        self.xdata, self.ydata = [], []
        self.init()
        plt.draw()
        plt.show(block=False)

    def data_gen(self, t=0):
        sub_sec = None
        result = []
        sec_names = []
        param_name = ['v']
        for neuron_name, n in self.nrn.neurons.iteritems():
            sec_name, sub_sec = n.get_selected_sub_section()
            if sub_sec != None:
                result.append(sub_sec.get_param('v')[0])
                sec_names.append('v ' + neuron_name + ' ' + sec_name)
        if len(result) != 0:
            return self.nrn.get_time(), result, sec_names
        else:
            return 0, [-70.0], sec_names

    def init(self):
        self.axes.set_title('Voltage in selected sections',fontsize=16, fontweight='bold')
        self.axes.set_xlabel('Time (s)')
        self.axes.set_ylabel('Voltage (V)')
        self.axes.set_ylim(-70.1, 70.1)
        self.axes.set_xlim(0, self.nrn.get_dt() * 10)
        del self.xdata[:]
        del self.ydata[:]
        return self.lines

def graph_run(nrn):
    plt.ion()
    return Graph(nrn)

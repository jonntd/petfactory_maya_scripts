from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui

import petfactory.gui.simple_widget as simple_widget
reload(simple_widget)

import dotprod_flare
#import petfactory.animation.nuke_crop.dotprod_flare as dotprod_flare
reload(dotprod_flare)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
class Widget(QtGui.QWidget):
    
    def __init__(self, parent=None):

        super(Widget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.setGeometry(50, 50, 200, 200)
        self.setWindowTitle('Dot Product')
        self.bg_color = QtGui.QColor(68,68,68)

        p = self.palette()
        p.setColor(self.backgroundRole(), self.bg_color)
        self.setPalette(p)

        
        self.equations = {}
        self.equations['linear'] = dotprod_flare.linear
        self.equations['easeInOutCubic'] = dotprod_flare.easeInOutCubic
        self.equations['easeOutCubic'] = dotprod_flare.easeOutCubic
        self.equations['easeInCubic'] = dotprod_flare.easeInCubic

        vbox = QtGui.QVBoxLayout()
        vbox.setContentsMargins(5,5,5,5)
        self.setLayout(vbox)

        self.combo = QtGui.QComboBox()
        self.curve_canvas = CurveCanvas(self.equations.get(self.combo.currentText()), self.bg_color)

        self.combo.addItems(self.equations.keys())
        self.combo.currentIndexChanged.connect(self.index_changed)
        self.combo.setCurrentIndex(3)

        vbox.addWidget(self.curve_canvas)
        vbox.addWidget(self.combo)

        self.min_spinbox = simple_widget.add_spinbox(label='Min', parent_layout=vbox, min=0, max=1, default=0, double_spinbox=True, decimals=3, singlestep=.05, label_width=40)
        self.min_spinbox.valueChanged.connect(self.min_spinbox_change)

        self.max_spinbox = simple_widget.add_spinbox(label='Max', parent_layout=vbox, min=0, max=1, default=1, double_spinbox=True, decimals=3, singlestep=.05, label_width=40)
        self.max_spinbox.valueChanged.connect(self.max_spinbox_change)

        self.size_mult_spinbox = simple_widget.add_spinbox(label='Multiplier', parent_layout=vbox, min=0, max=10, default=1, double_spinbox=True, decimals=3, singlestep=.1, label_width=40)

        self.process_data_btn = QtGui.QPushButton('Dot Product')
        vbox.addWidget(self.process_data_btn)
        self.process_data_btn.clicked.connect(self.process_data)


    def process_data(self):

        equation = self.equations.get(self.combo.currentText())
        old_min = self.min_spinbox.value()
        old_max = self.max_spinbox.value()
        multiplier = self.size_mult_spinbox.value()
        dotprod_flare.get_dot_prod(old_min, old_max, equation, multiplier)


    def index_changed(self, index):
        self.curve_canvas.change_equation(self.equations.get(self.combo.currentText()))
        self.curve_canvas.repaint()

    def min_spinbox_change(self, val):

        limit = self.max_spinbox.value()-.05
        if val > limit:
            self.min_spinbox.blockSignals(True)
            self.min_spinbox.setValue(limit)
            self.min_spinbox.blockSignals(False)
            val = limit

        self.curve_canvas.change_min(val)
        self.curve_canvas.repaint()



    def max_spinbox_change(self, val):

        limit = self.min_spinbox.value()+.05
        if val < limit:
            self.max_spinbox.blockSignals(True)
            self.max_spinbox.setValue(limit)
            self.max_spinbox.blockSignals(False)
            val = limit

        self.curve_canvas.change_max(val)
        self.curve_canvas.repaint()



class CurveCanvas(QtGui.QWidget):
    
    def __init__(self, equation, bg_color):
        super(CurveCanvas, self).__init__()
        
        self.setMinimumHeight(20)
        self.equation = equation
        self.min = 0.0
        self.max = 1.0
        self.bg_color = bg_color
        self.grid_color = self.bg_color.lighter(110)
        self.line_color = self.bg_color.lighter(130)
        self.dot_color = self.bg_color.lighter(160)

    def paintEvent(self, e):

        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawPoints(qp)
        qp.end()
        
    def drawPoints(self, qp):
      
        width, height = self.size().toTuple()
        offset = 6

        pen = QtGui.QPen()
        pen.setColor(self.grid_color)
        pen.setWidth(1)
        qp.setPen(pen)

        num = 11
        inc = 1.0/(num-1)
        for i in range(num):
            x = i*inc*(width-offset*2)+offset
            y = i*inc*(height-offset*2)+offset
            qp.drawLine(x,offset, x, height-offset)
            qp.drawLine(offset, y, width-offset, y)
        
        
        if self.equation is None:
            return

        old_min = self.min
        old_max = self.max

        pen.setColor(self.line_color)
        qp.setPen(pen)

        for i in range(num-1):

            u1 = i * inc
            u2 = (i+1) * inc
            x1 = u1 * (width-offset*2) + offset
            x2 = u2 * (width-offset*2) + offset

            uy1 = min(1.0, max(0, dotprod_flare.lerp(old_min,0,old_max,1,u1)))
            uy2 = min(1.0, max(0, dotprod_flare.lerp(old_min,0,old_max,1,u2)))
            y1 = self.equation(uy1, 0, 1.0, 1.0) * (height-offset*2) + offset
            y2 = self.equation(uy2, 0, 1.0, 1.0) * (height-offset*2) + offset
            qp.drawLine(x1, -y1+height, x2, -y2+height)


        pen.setWidth(4)
        pen.setColor(self.dot_color)
        qp.setPen(pen)

        for i in range(num):
            u = i * inc
            uy = min(1.0,max(0, dotprod_flare.lerp(old_min,0,old_max,1,u)))
            x = u * (width-offset*2) + offset
            y = self.equation(uy, 0, 1.0, 1.0) * (height-offset*2) + offset
            qp.drawPoint(x, -y+height)

    def change_equation(self, equation):
        self.equation = equation

    def change_min(self, val):
        self.min = val

    def change_max(self, val):
        self.max = val

def show():
    win = Widget(parent=maya_main_window())
    win.show()
    return win

'''
try:
    win.close()
    
except NameError:
    print('No win to close')
    
win = show()
win.move(100,150)
'''
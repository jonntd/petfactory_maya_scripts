#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
from PySide import QtGui, QtCore


class BaseWin(QtGui.QWidget):
    
    def __init__(self):
        super(BaseWin, self).__init__() 

        self.setGeometry(200, 400, 300, 300)
        self.setWindowTitle('Test')

        self.iconWidth = 50
        self.iconHeight = 18
        self.iconStrokeWidth = 1
        self.iconEdgeOffset = 4
        self.iconBgColor = QtGui.QColor(220, 220, 220, 0)
        self.iconActiveColor = QtGui.QColor(240, 170, 50, 255)

        # layout
        vbox = QtGui.QVBoxLayout(self)

        self.model = QtGui.QStandardItemModel()
        self.treeView = QtGui.QTreeView()
        self.treeView.setIconSize(QtCore.QSize(self.iconWidth, self.iconHeight))
        self.treeView.setModel(self.model)
        vbox.addWidget(self.treeView)

        self.populateTreeview('Roof 25%', .25, self.model.invisibleRootItem(), self.model)
        self.populateTreeview('Door 50%', .50, self.model.invisibleRootItem(), self.model)
        self.populateTreeview('Wheel 75%', .75, self.model.invisibleRootItem(), self.model)

    def createIcon(self, vertValue):

        barWidth = vertValue * self.iconWidth

        pixmap = QtGui.QPixmap(self.iconWidth, self.iconHeight)
        pixmap.fill(self.iconBgColor)

        iconRect = QtCore.QRect(0, self.iconEdgeOffset, self.iconWidth-1, self.iconHeight-self.iconEdgeOffset*2)
        barRect = QtCore.QRect(0, self.iconEdgeOffset, barWidth-1, self.iconHeight-self.iconEdgeOffset*2)

        painter = QtGui.QPainter(pixmap)
        painter.fillRect(barRect, self.iconActiveColor)

        painter.setBrush(QtCore.Qt.NoBrush)
        pen = QtGui.QPen()
        pen.setBrush(self.iconActiveColor)
        pen.setWidth(self.iconStrokeWidth )
        painter.setPen(pen)
        painter.drawRect(iconRect)

        painter.end()
        return QtGui.QIcon(pixmap)

    def populateTreeview(self, name, vertValue, parent, model):

        item = QtGui.QStandardItem(name)
        item.setSizeHint(QtCore.QSize(100, self.iconHeight))
        item.setIcon(self.createIcon(vertValue))
        parent.appendRow(item)

def main():
    
    app = QtGui.QApplication(sys.argv)
    baseWin = BaseWin()
    baseWin.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
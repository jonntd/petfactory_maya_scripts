#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
from PySide import QtGui, QtCore

class Example(QtGui.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        
        self.setGeometry(60, 100, 250, 150)
        self.setWindowTitle('Icon')
        
        hbox = QtGui.QHBoxLayout(self)

        self.nameDict = {'A':['one', 'two', 'three'], 'B':['four', 'five'], 'C':['six', 'seven', 'eight', 'nine']}

        self.combobox = QtGui.QComboBox()
        
        itemDelegate = QtGui.QStyledItemDelegate()
        self.combobox.setItemDelegate(itemDelegate); 

        self.combobox.setStyleSheet('''QComboBox QAbstractItemView::item { min-height: 20px;}''')
        hbox.addWidget(self.combobox)
        self.combobox.currentIndexChanged.connect(self.comboboxCurrentIndexChanged)

        self.model = QtGui.QStandardItemModel()
        self.model.dataChanged.connect(self.treeviewDataChanged)

        self.treeview = QtGui.QTreeView()
        self.treeview.setModel(self.model)
        hbox.addWidget(self.treeview)

        self.show()
        self.populateCombobox(self.nameDict.keys())

    def comboboxCurrentIndexChanged(self, index):

        key = self.combobox.currentText()
        nameList = self.nameDict.get(key)
        self.populateModel(nameList)

    def cleanModel(self, model):
         numRows = model.rowCount()
         for row in range(numRows):
             model.removeRow(0)

    def populateModel(self, nameList):
        
        self.cleanModel(self.model)
        rootItem = self.model.invisibleRootItem()

        
        for name in nameList:
            item = QtGui.QStandardItem(name)
            item.setSizeHint(QtCore.QSize(0,20))
            #item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            rootItem.appendRow(item)

        self.model.blockSignals(True)
        numRows = self.model.rowCount()
        if numRows > 0:
            index = self.model.index(0,0)
            self.model.setData(index, '{} -> XXX'.format(nameList[0]))
        self.model.blockSignals(False)
        

    def populateCombobox(self, nameList):
        
        self.combobox.addItems(nameList)

    def treeviewDataChanged(self, indexTopLeft, indexBottomRight):
        print(indexTopLeft, indexBottomRight)

    def setIndex(self, index):
        self.combobox.setCurrentIndex(index)


        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()

    '''
    fruitList = ['Orange', 'Apple', 'Pear']
    ex.populateCombobox(fruitList)

    try:
        index = fruitList.index('Pear')
    except ValueError as e:
        print(e)
        return
    
    ex.setIndex(index)
    '''
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
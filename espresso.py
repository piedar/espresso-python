#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Copyright 2013 Benn Snyder
Espresso is a simple app that sits in the system tray and keeps the computer awake when activated.
Espresso is freely available under the terms of the GNU Public License, version 3.  The license appears in GPLv3.txt.
'''

import os
import sys
try:
	from PySide import QtCore, QtGui, QtSvg
except ImportError:
	from PyQt4 import QtCore, QtGui, QtSvg


class TrayIcon(QtGui.QSystemTrayIcon):
	def __init__(self, inhibitor):
		QtGui.QSystemTrayIcon.__init__(self)
		self.inhibitor = inhibitor
		self.empty = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "Empty_Cup.svg"))
		self.full = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "Full_Cup.svg"))
		self.setIcon(self.empty)
		self.setToolTip("Espresso - click to toggle, middle-click to quit")
		self.activated.connect(self.Activate)

	def Activate(self, reason):
		if reason == QtGui.QSystemTrayIcon.Trigger:
			self.inhibitor.Toggle()
			if self.inhibitor.Inhibited:
				self.setIcon(self.full)
			else:
				self.setIcon(self.empty)
		
		if reason == QtGui.QSystemTrayIcon.MiddleClick:
			self.inhibitor.UnInhibit()
			self.deleteLater() # prevents PyQt4 segfault
			QtGui.QApplication.quit()


if __name__ == "__main__":
	import platform
	if platform.system() == "Linux":
		from inhibitors import DBusInhibitor as SleepInhibitor
	elif platform.system() == "Windows" and sys.getwindowsversion().major >= 6 and sys.getwindowsversion().minor >= 1:
		from inhibitors import Win7Inhibitor as SleepInhibitor
	else:
		print("Platform not supported!")
		sys.exit(1)
	
	app = QtGui.QApplication(sys.argv)
	if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
		QtGui.QMessageBox.critical(None, QtCore.QObject.tr(app, "Espresso"), QtCore.QObject.tr(app, "No system tray available"))
		sys.exit(1)
	icon = TrayIcon(SleepInhibitor());
	icon.show()
	sys.exit(app.exec_())

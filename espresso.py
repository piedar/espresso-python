#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Copyright 2013 Benn Snyder
Espresso is a simple app that sits in the system tray and keeps the computer awake when activated.
Espresso is freely available under the terms of the GNU Public License, version 3.  The license appears in GPLv3.txt.
'''

import os
import sys
import dbus
try:
	from PySide import QtCore, QtGui
except ImportError:
	from PyQt4 import QtCore, QtGui # todo: use QtDBus


class TrayIcon(QtGui.QSystemTrayIcon):
	def __init__(self):
		QtGui.QSystemTrayIcon.__init__(self)
		self.empty = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "Empty_Cup.svg"))
		self.full = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "Full_Cup.svg"))
		
		self.pm = dbus.SessionBus().get_object("org.freedesktop.PowerManagement", "/org/freedesktop/PowerManagement/Inhibit")
		
		self.inhibit = None
		self.setIcon(self.empty)
		self.setToolTip("Espresso - click to toggle, middle-click to quit")
		self.activated.connect(self.Activate)

	def Activate(self, reason):
		if reason == QtGui.QSystemTrayIcon.Trigger:
			if self.inhibit is None:
				self.inhibit = self.pm.Inhibit("Espresso", "Inhibited by user")
				self.setIcon(self.full)
			else:
				self.pm.UnInhibit(self.inhibit)
				self.setIcon(self.empty)
				self.inhibit = None
		
		if reason == QtGui.QSystemTrayIcon.MiddleClick:
			if self.inhibit is not None:
				self.pm.UnInhibit(self.inhibit)
			self.deleteLater() # prevents PyQt4 segfault
			QtGui.QApplication.quit()


if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)

	if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
		QtGui.QMessageBox.critical(None, QtCore.QObject.tr(app, "Espresso"), QtCore.QObject.tr(app, "No system tray available"))
		sys.exit(1)
	
	icon = TrayIcon();
	icon.show()
	sys.exit(app.exec_())

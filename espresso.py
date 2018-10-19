#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Copyright 2013 Benn Snyder
Espresso keeps your computer awake from the system tray.
Espresso is freely available under the terms of the GNU Public License, version 3.  The license appears in GPLv3.txt.
'''

import os
import sys
from threading import Timer
try:
	from PySide import QtCore, QtGui, QtSvg
except ImportError:
	from PyQt5 import QtCore, QtGui, QtSvg, QtWidgets


class TrayIcon(QtWidgets.QSystemTrayIcon):
	def __init__(self, inhibitor, parent):
		super().__init__(parent)

		self.ICON_EMPTY_CUP     = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "Empty_Cup.svg"))
		self.ICON_FULL_CUP      = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "Full_Cup.svg"))
		self.ICON_CRYSTAL_CLOCK = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "Crystal_Clock.svg"))
		self.ICON_CLOSE         = self.parent().style().standardIcon(QtWidgets.QStyle.SP_DialogCloseButton)

		self.inhibitor = inhibitor
		self.timer = Timer(0, self.Event) # default timer never runs
		self.UnInhibit()
		self.setToolTip("Espresso - click to toggle, middle-click to quit")
		self.setContextMenu(self.BuildMenu())
		self.activated.connect(self.Event)

	def BuildMenu(self):
		menu = QtWidgets.QMenu()

		inhibit_menu = menu.addMenu(self.ICON_CRYSTAL_CLOCK, "Inhibit for")
		for minutes in [1, 5, 10, 15, 30]:
			suffix = "s" if minutes > 1 else ""
			inhibit_menu.addAction(str(minutes)+" minute"+suffix).triggered.connect(lambda m = minutes : self.Inhibit(m))
		for hours in [1, 2, 5]:
			suffix = "s" if hours > 1 else ""
			inhibit_menu.addAction(str(hours)+" hour"+suffix).triggered.connect(lambda m = hours*60 : self.Inhibit(m))
		inhibit_menu.addAction("Indefinitely").triggered.connect(self.Inhibit)

		menu.addAction(self.ICON_CLOSE, "Quit").triggered.connect(self.Quit)
		return menu

	def Event(self, reason):
		if reason == QtWidgets.QSystemTrayIcon.Trigger:
			if not self.inhibitor.Inhibited:
				self.Inhibit()
			else:
				self.UnInhibit()
		elif reason == QtWidgets.QSystemTrayIcon.MiddleClick:
			self.Quit()

	def Inhibit(self, timeout_minutes = None):
		self.timer.cancel()
		if timeout_minutes is not None:
			self.timer = Timer(timeout_minutes*60, self.UnInhibit)
			self.timer.start()
		self.setIcon(self.ICON_FULL_CUP)
		self.inhibitor.Inhibit()

	def UnInhibit(self):
		self.timer.cancel()
		self.setIcon(self.ICON_EMPTY_CUP)
		self.inhibitor.UnInhibit()

	def Quit(self):
		self.UnInhibit()
		self.deleteLater() # prevents PyQt4 segfault
		self.parent().quit()


if __name__ == "__main__":
	import inhibitors

	app = QtWidgets.QApplication(sys.argv)
	if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
		QtGui.QMessageBox.critical(None, QtCore.QObject.tr(app, "Espresso"), QtCore.QObject.tr(app, "No system tray available"))
		sys.exit(1)
	icon = TrayIcon(inhibitors.AutoSelect(), app);
	icon.show()
	sys.exit(app.exec_())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Copyright 2013 Benn Snyder
Espresso is a simple app that sits in the system tray and keeps the computer awake when activated.
Espresso is freely available under the terms of the GNU Public License, version 3.  The license appears in GPLv3.txt.
'''

# This file contains an Inhibitor interface and Inhibitor implementations for various platforms

from abc import ABCMeta, abstractmethod


class Inhibitor(metaclass=ABCMeta):
	def __init__(self):
		self.inhibited = None # Children: set to None when not inhibited
	
	@property
	def Inhibited(self):
		return self.inhibited is not None
	
	def Toggle(self):
		if not self.Inhibited:
			self.Inhibit()
		else:
			self.UnInhibit()
	
	@abstractmethod
	def Inhibit(self):
		pass
	
	@abstractmethod
	def UnInhibit(self):
		pass

class DBusInhibitor(Inhibitor):
	def __init__(self):
		import dbus
		Inhibitor.__init__(self)
		self.pm = dbus.SessionBus().get_object("org.freedesktop.PowerManagement", "/org/freedesktop/PowerManagement/Inhibit")
		
	def Inhibit(self):
		if not Inhibited:
			self.inhibited = self.pm.Inhibit("Espresso", "Inhibited by user")
	
	def UnInhibit(self):
		if Inhibited:
			self.pm.UnInhibit(self.inhibited)
			self.inhibited = None

class Win7Inhibitor(Inhibitor):
	# _POWER_REQUEST_TYPE enum from WinNT.h
	(
	PowerRequestDisplayRequired,
	PowerRequestSystemRequired,
	PowerRequestAwayModeRequired,
	PowerRequestExecutionRequred, # Windows 8 only
	) = map(int, range(4))
	
	def __init__(self):
		global ctypes
		import ctypes
		Inhibitor.__init__(self)
		self.request = ctypes.windll.kernel32.PowerCreateRequest(None) # todo: reason
	
	def Inhibit(self):
		if not self.Inhibited:
			result = ctypes.windll.kernel32.PowerSetRequest(self.request, self.PowerRequestSystemRequired)
			if result != 0:
				self.inhibited = True
			else:
				print("Inhibit failed!")
			
	def UnInhibit(self):
		if self.Inhibited:
			result = ctypes.windll.kernel32.PowerClearRequest(self.request, self.PowerRequestSystemRequired)
			if result != 0:
				self.inhibited = None
			else:
				print("UnInhibit failed!")

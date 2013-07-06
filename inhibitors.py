#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Copyright 2013 Benn Snyder
Espresso keeps your computer awake from the system tray.
Espresso is freely available under the terms of the GNU Public License, version 3.  The license appears in GPLv3.txt.
'''

from abc import ABCMeta, abstractmethod


def AutoSelect():
	import platform
	if platform.system() == "Linux":
		return DBusInhibitor()
	elif platform.system() == "Windows" and sys.getwindowsversion().major >= 6 and sys.getwindowsversion().minor >= 1:
		return Win7Inhibitor()
	else:
		raise NotImplementedError("Platform not supported")

# Implementations need only implement the methods marked with the `@abstractmethod` decorator and make sure `self.inhibited` is `None` only when not inhibited.
class SleepInhibitor(metaclass=ABCMeta):
	"""
	A SleepInhibitor implementation can be used to keep a machine awake in one of two ways.
	
	Explicitly:
		inhibitor = ConcreteInhibitor()
		inhibitor.Inhibit()
		# AWAKE
		inhibitor.UnInhibit() # or inhibitor.Toggle()
		
	In a `with` statement:
		with ConcreteInhibitor() as inhibitor:
			# AWAKE
	"""
	
	def __init__(self):
		self.inhibited = None # Attention Children: set to None when not inhibited
	
	def __del__(self):
		self.UnInhibit()
		
	def __enter__(self):
		self.Inhibit()
		return self
	
	def __exit__(self, type, value, traceback):
		self.UnInhibit()
	
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

class DBusInhibitor(SleepInhibitor):
	def __init__(self):
		super().__init__()
		import dbus
		self.pm = dbus.SessionBus().get_object("org.freedesktop.PowerManagement", "/org/freedesktop/PowerManagement/Inhibit")
		
	def Inhibit(self):
		if not self.Inhibited:
			self.inhibited = self.pm.Inhibit("Espresso", "Inhibited by user")
	
	def UnInhibit(self):
		if self.Inhibited:
			self.pm.UnInhibit(self.inhibited)
			self.inhibited = None

class Win7Inhibitor(SleepInhibitor):
	# _POWER_REQUEST_TYPE enum from WinNT.h
	(
	PowerRequestDisplayRequired,
	PowerRequestSystemRequired,
	PowerRequestAwayModeRequired,
	PowerRequestExecutionRequred, # Windows 8 only
	) = map(int, range(4))
	
	def __init__(self):
		super().__init__()
		global ctypes
		import ctypes
		self.request = ctypes.windll.kernel32.PowerCreateRequest(None) # todo: reason
	
	def Inhibit(self):
		if not self.Inhibited:
			result = ctypes.windll.kernel32.PowerSetRequest(self.request, self.PowerRequestSystemRequired)
			if result != 0: # yes, this function returns 0 on failure
				self.inhibited = True
			else:
				raise OSError(result, "SetPowerRequest() failed")
			
	def UnInhibit(self):
		if self.Inhibited:
			result = ctypes.windll.kernel32.PowerClearRequest(self.request, self.PowerRequestSystemRequired)
			if result != 0:
				self.inhibited = None
			else:
				raise OSError(result, "PowerClearRequest() failed")

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from Components.Label import Label
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import *
import sys, os
from .Config import *
from skin import loadSkin
from enigma import getDesktop

if getDesktop(0).size().width() == 1920:
	loadSkin("/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Skin/skinFHD.xml")
	giopath = '/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/'
else:
	loadSkin("/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Skin/skinhd.xml")
	giopath = '/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/'


class MenuListSelect(MenuList):

    def __init__(self, list, enableWrapAround = True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        screenwidth = getDesktop(0).size().width()
        if screenwidth and screenwidth == 1920:
            self.l.setFont(0, gFont('Regular', 32))
            self.l.setFont(1, gFont('Regular', 24))
            self.l.setItemHeight(80)
        else:
            self.l.setFont(0, gFont('Regular', 20))
            self.l.setFont(1, gFont('Regular', 14))
            self.l.setItemHeight(50)

class ListSelect:

	def __init__(self):
		pass

	def readSaveList(self):
		try:
			jw = open('/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Moduli/Settings/Select')
			jjw = jw.readlines()
			jw.close()
			list = []
			for x in jjw:
				try:
					jx = x.split('---')
					list.append((jx[0], jx[1].strip()))
				except:
					pass
			return list
		except:
			pass

	def SaveList(self, list):
		jw = open('/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Moduli/Settings/Select', 'w')
		for dir, name, value in list:
			if value == '1':
				jw.write(dir + '---' + name + '\n')
		jw.close()

	def readBouquetsList(self, pwd, bouquetname):
		try:
			f = open(pwd + '/' + bouquetname)
		except Exception as e:
			print(e)
			return
		ret = []
		while True:
			line = f.readline()
			if line == '':
				break
			if line[:8] != '#SERVICE':
				continue
			tmp = line.strip().split(':')
			line = tmp[len(tmp) - 1]
			filename = None
			if line[:12] == 'FROM BOUQUET':
				tmp = line[13:].split(' ')
				filename = tmp[0].strip('"')
			else:
				filename = line
			if filename:
				try:
					fb = open(pwd + '/' + filename)
				except Exception as e:
					continue
				tmp = fb.readline().strip()
				if tmp[:6] == '#NAME ':
					ret.append([filename, tmp[6:]])
				else:
					ret.append([filename, filename])
				fb.close()
		return ret

	def readBouquetsTvList(self, pwd):
		return self.readBouquetsList(pwd, 'bouquets.tv')

	def TvList(self):
		jload = self.readSaveList()
		self.bouquetlist = []
		for x in self.readBouquetsTvList('/etc/enigma2'):
			value = '0'
			try:
				for j, jx in jload:
					if j == x[0] and jx.find(x[1]) != -1:
						value = '1'
						break
			except:
				pass
			self.bouquetlist.append((x[0], x[1], value))
		return self.bouquetlist

class MenuSelect(Screen, ConfigListScreen):

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self.ListSelect = ListSelect()
		self['autotimer'] = Label('')
		self['namesat'] = Label('')
		self['text'] = Label('')
		self['dateDow'] = Label('')
		self['Green'] = Pixmap()
		self['Blue'] = Pixmap()
		self['Yellow'] = Pixmap()
		self['Green'].hide()
		self['Yellow'].hide()
		self['Blue'].hide()
		self['Key_Lcn'] = Label('')
		self['key_red'] = Label(_('Exit'))
		self['Key_green'] = Label(_('Installed list:'))
		self['Key_Personal'] = Label('')
		self['A'] = MenuListSelect([])
		self['B'] = MenuListSelect([])
		self['B'].selectionEnabled(1)
		self.Info()
		self.Menu()
		self.MenuA()
		self['actions'] = ActionMap(['OkCancelActions', 'ShortcutActions', 'WizardActions', 'ColorActions', 'SetupActions', 'NumberActions', 'MenuActions', 'HelpActions', 'EPGSelectActions'],
			{'ok': self.OkSelect,
			 'up': self.keyUp,
			 'down': self.keyDown,
			 'cancel': self.Uscita,
			 'nextBouquet': self['B'].pageUp,
			 'prevBouquet': self['B'].pageDown,
			 'red': self.Uscita}
			 , -1)

	def Info(self):
		Type, AutoTimer, Personal, NumberSat, NameSat, Date, NumberDtt, DowDate, NameInfo = Load()
		if str(Date) == '0':
			newdate = ''
		else:
			newdate = ' - ' + ConverDate(Date)
		if str(DowDate) == '0':
			newDowDate = _('Last Update: Never')
		else:
			newDowDate = _('Last Update:') + DowDate
		self['namesat'].setText(NameInfo + newdate)
		self['dateDow'].setText(newDowDate)

	def Uscita(self):
		self.close()

	def keyUp(self):
		self['B'].up()

	def keyDown(self):
		self['B'].down()

	def hauptListEntry(self, dir, name, value):
		res = [(dir, name, value)]
		icon = '/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/key_red.png'
		if value == '1':
			icon = '/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/key_green.png'
		try:
			name = name.split('   ')[0]
		except:
			pass
		res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 11), size=(20, 20), png=loadPic(icon, 20, 20, 0, 0, 0, 1)))
		res.append(MultiContentEntryText(pos=(80, 7), size=(625, 45), font=0, text=name, flags=RT_HALIGN_LEFT))
		res.append(MultiContentEntryText(pos=(0, 0), size=(0, 0), font=0, text=dir, flags=RT_HALIGN_LEFT))
		res.append(MultiContentEntryText(pos=(0, 0), size=(0, 0), font=0, text=value, flags=RT_HALIGN_LEFT))
		return res

	def hauptListEntryA(self, name):
		res = [name]
		try:
			name = name.split('   ')[0]
		except:
			pass
		res.append(MultiContentEntryText(pos=(20, 7), size=(625, 45), font=0, text=name, flags=RT_HALIGN_LEFT))
		return res

	def MenuA(self):
		self.jB = []
		lista = self.ListSelect.readSaveList()
		if lista:
			for dir, name in lista:
				self.jB.append(self.hauptListEntryA(name))
		self['A'].setList(self.jB)
		if not self.jB:
			self['text'].setText(_('Please select\nwhat you want\nto keep!'))
		else:
			self['text'].setText(' ')
		self['B'].selectionEnabled(1)
		self['A'].selectionEnabled(0)

	def Menu(self):
		self.jA = []
		for dir, name, value in self.ListSelect.TvList():
			if not name.lower().find('dtt') != -1 and name != 'Favourites (TV)':
				self.jA.append(self.hauptListEntry(dir, name, value))
		self['B'].setList(self.jA)

	def OkSelect(self):
		NewName = self['B'].getCurrent()[0][1]
		NewDir = self['B'].getCurrent()[0][0]
		self.list = []
		for dir, name, value in self.ListSelect.TvList():
			if dir == NewDir and name == NewName:
				if value == '0':
					self.list.append((dir, name, '1'))
			elif value == '1':
				self.list.append((dir, name, '1'))
		self.ListSelect.SaveList(self.list)
		self.Menu()
		self.MenuA()

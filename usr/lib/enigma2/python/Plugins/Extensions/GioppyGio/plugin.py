from Components.Label import Label
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Screens.Console import Console
from Components.Pixmap import Pixmap
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.MultiContent import MultiContentEntryText
from enigma import *
from Components.ScrollLabel import ScrollLabel
from Tools.BoundFunction import boundFunction
from Components.Language import language
from os import environ, listdir, remove, rename, system, popen
import gettext
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from enigma import getDesktop
from skin import loadSkin
from enigma import eTimer, eDVBCI_UI, eListboxPythonStringContent, eListboxPythonConfigContent
import time
from Tools.LoadPixmap import LoadPixmap
import xml.dom.minidom
import pprint
from xml.dom import Node, minidom
#import requests
from ServiceReference import ServiceReference
import os, sys
from os import listdir
from twisted.web.client import downloadPage 
import urllib
from enigma import *
import sys,os
from Moduli.Setting import *
from Moduli.Config import *
from Moduli.Select import *
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
plugin_path = '/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/'
from enigma import addFont
global giopath
global Index
plugin='[GioppyGio] '
lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("GioppyGio", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/GioppyGio/locale/"))

def _(txt):
	t = gettext.dgettext("GioppyGio", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

def translateBlock(block):
	for x in TranslationHelper:
		if block.__contains__(x[0]):
			block = block.replace(x[0], x[1])
	return block

if getDesktop(0).size().width() == 1920:
	loadSkin("/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Skin/skinFHD.xml")
	giopath = '/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/'
else:
	loadSkin("/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Skin/skinhd.xml")
	giopath = '/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/'


class MenuListGioB(MenuList):

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
class MenuListGioA(MenuList):

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

class MenuGio(Screen):

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "HelpActions","EPGSelectActions"], { 
                 "ok"    : self.keyOK,
                 "up"    : self.keyUp,
                 "down"  : self.keyDown,
                 "blue"  : self.Auto,
                 "yellow": self.Select,
                 "cancel": self.exitplug,
                 "left"  : self.keyRightLeft,
                 "right" : self.keyRightLeft,
                 "menu"  : self.keyMenu,
                 "red"   : self.exitplug}, -1)
		self['autotimer'] = Label("")
		self['namesat'] = Label("")
		self['text'] = Label("")
		self['dateDow'] = Label("")
		self['Green'] = Pixmap()
		self['Blue'] = Pixmap()
		self['Yellow'] = Pixmap()
		self['Yellow'].show()
		self['Menu'] = Pixmap()
		self['Menu'].show()
		self['Blue'].show()
		self['Key_Red'] = Label(_('Exit'))
		self['Key_Green'] = Label(_('Installed list:'))
		self['Key_Personal'] = Label('')
		self['Key_Menu'] = Label(_('Picons'))
		self['A'] = MenuListGioA([])
		self['B'] = MenuListGioB([])
		self['B'].selectionEnabled(1)
		self['A'].selectionEnabled(1)
		self.currentlist = 'B'
		self.ServerOn = True
		self.DubleClick = True
		self.MenuA()
		self.List = DownloadSetting()
		self.MenuB()
		self.iTimer = eTimer()
		self.iTimer.callback.append(self.keyRightLeft)
		self.iTimer.start(1000,True)
		self.iTimer1 = eTimer()
		self.iTimer1.callback.append(self.StartSetting)
		self.OnWriteAuto = eTimer()
		self.OnWriteAuto.callback.append(self.WriteAuto)
		self.StopAutoWrite = False
		self.ExitPlugin = eTimer()
		self.ExitPlugin.callback.append(self.PluginClose)
		self.onShown.append(self.ReturnSelect)
		self.onShown.append(self.Info)

	def keyMenu(self):
		self.session.open(picons)
	def PluginClose(self):
		try:
			self.ExitPlugin.stop()
		except:
			pass

		self.close()

	def exitplug(self):
		if self.DubleClick:
			self.ExitPlugin.start(10,True)
			self.DubleClick = False
		else:
			self.PluginClose()

	def Select(self):
		Type,AutoTimer,Personal,NumberSat,NameSat,Date,NumberDtt,DowDate,NameInfo = Load()
		if str(Personal).strip() == '0':
			self['Key_Personal'].setText(_("Favourite: Yes"))
			Personal = '1'
			self.session.open(MenuSelect)
		else:
			self['Key_Personal'].setText(_("Favourite: No"))
			Personal = '0'
		WriteSave(Type,AutoTimer,Personal,NumberSat,NameSat,Date,NumberDtt,DowDate,NameInfo)

	def ReturnSelect(self):
		Type, AutoTimer,Personal,NumberSat,NameSat,Date,NumberDtt,DowDate,NameInfo= Load()
		if not os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Moduli/Settings/Select' ) or os.path.getsize('/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Moduli/Settings/Select' ) < 20:
			self['Key_Personal'].setText(_("Favourite: No"))
			WriteSave(Type, AutoTimer,'0' , NumberSat,NameSat,Date,NumberDtt,DowDate,NameInfo)

	def Auto(self):
		if self.StopAutoWrite:
			return
		self.StopAutoWrite = True
		iTimerClass.StopTimer()
		self.Type,AutoTimer,self.Personal,self.NumberSat,self.NameSat,self.Date,self.NumberDtt,self.DowDate,self.NameInfo= Load()
		if int(AutoTimer) == 0:
			self['autotimer'].setText(_("Auto Update: Yes"))
			self.jAutoTimer = 1
			iTimerClass.TimerSetting()
		else:
			self['autotimer'].setText(_("Auto Update: No"))
			self.jAutoTimer = 0
		self.OnWriteAuto.start(1000,True)

	def WriteAuto(self):
		self.StopAutoWrite = False
		WriteSave(self.Type, self.jAutoTimer,self.Personal,self.NumberSat,self.NameSat,self.Date,self.NumberDtt,self.DowDate,self.NameInfo)

	def Info(self):
		Type, AutoTimer,Personal,NumberSat,NameSat,Date,NumberDtt,DowDate,NameInfo = Load()
		if int(AutoTimer) == 0:
			TypeTimer = 'No'
		else:
			TypeTimer = 'Yes'
		if int(Personal) == 0:
			jPersonal = 'No'
		else:
			jPersonal = 'Yes'
		if str(Date) == '0':
			newdate = ('')
		else:
			newdate = (' - '+ConverDate(Date))
		if str(DowDate) == '0':
			newDowDate = _("Last Update: Never")
		else:
			newDowDate = _('Last Update: ') + DowDate
		self['Key_Personal'].setText(_("Favourite:")+jPersonal)
		self['autotimer'].setText(_("Auto Update:")+TypeTimer)
		self['namesat'].setText(NameInfo + newdate)
		self['dateDow'].setText(newDowDate)

	def hauptListEntryMenuA(self, name, type):
		res = [(name, type)]
		res.append(MultiContentEntryText(pos=(60, 7), size=(230, 45), font=0, text=name, flags=RT_HALIGN_CENTER))
		res.append(MultiContentEntryText(pos=(0, 0), size=(8, 0), font=0, text=type, flags=RT_HALIGN_LEFT))
		return res

	def hauptListEntryMenuB(self, NumberSat, Name, jData, NumberDtt):
		res = [(NumberSat, Name, jData, NumberDtt)]
		if NumberDtt =='xx':
			res.append(MultiContentEntryText(pos=(10, 5), size=(750, 35), font=0, text=Name, flags=RT_HALIGN_LEFT))
			res.append(MultiContentEntryText(pos=(0, 0), size=(0, 0), font=0, text=jData, flags=RT_HALIGN_LEFT))
			res.append(MultiContentEntryText(pos=(10, 5), size=(460, 35), font=0, text=Name, flags=RT_HALIGN_LEFT))
			res.append(MultiContentEntryText(pos=(470, 5), size=(120, 35), font=0, text=jData, flags=RT_HALIGN_LEFT))
			res.append(MultiContentEntryText(pos=(0, 0), size=(0, 0), font=0, text=NumberDtt, flags=RT_HALIGN_LEFT))
			res.append(MultiContentEntryText(pos=(0, 0), size=(0, 0), font=0, text=NumberSat, flags=RT_HALIGN_LEFT))
		else:

			res.append(MultiContentEntryText(pos=(20, 5), size=(850, 45), font=0, text=Name, flags=RT_HALIGN_LEFT))
			res.append(MultiContentEntryText(pos=(0, 0), size=(0, 0), font=0, text=jData, flags=RT_HALIGN_LEFT))
			res.append(MultiContentEntryText(pos=(20, 5), size=(650, 45), font=0, text=Name, flags=RT_HALIGN_LEFT))
			res.append(MultiContentEntryText(pos=(670, 5), size=(200, 45), font=0, text=jData, flags=RT_HALIGN_LEFT))
			res.append(MultiContentEntryText(pos=(0, 0), size=(0, 0), font=0, text=NumberDtt, flags=RT_HALIGN_LEFT))
			res.append(MultiContentEntryText(pos=(0, 0), size=(0, 0), font=0, text=NumberSat, flags=RT_HALIGN_LEFT))
		return res

	def MenuA(self):
		self.jA = []
		self.jA.append(self.hauptListEntryMenuA('Mono + DTT', 'mono'))
		self.jA.append(self.hauptListEntryMenuA('Dual + DTT', 'dual'))
		self.jA.append(self.hauptListEntryMenuA('Trial', 'trial'))
		self.jA.append(self.hauptListEntryMenuA('Quadri', 'quadri'))
		self.jA.append(self.hauptListEntryMenuA('Motor + DTT', 'motor'))
		self['A'].setList(self.jA)

	def MenuB(self):
		self.jB = []
		if not self.DubleClick:
			self.ServerOn = False
			self.jB.append(self.hauptListEntryMenuB('', _(''), 'xx', 'xx'))
			self.jB.append(self.hauptListEntryMenuB('', _(''), 'xx', 'xx'))
			self.jB.append(self.hauptListEntryMenuB('', _(''), 'xx', 'xx'))
			self.jB.append(self.hauptListEntryMenuB('', _(''), 'xx', 'xx'))
			self.jB.append(self.hauptListEntryMenuB('', _(''), 'xx', 'xx'))
			self['B'].setList(self.jB)
			return
		for NumberSat, NameSat, LinkSat, DateSat, NumberDtt, NameDtt, LinkDtt, DateDtt in self.List:
			if NameSat.lower().find(self["A"].getCurrent()[0][1]) != -1:
				if str(NameDtt) != '0':
					jData = str(DateSat)
					if int(DateDtt) > int(DateSat):
						jData = str(DateDtt)
					self.jB.append(self.hauptListEntryMenuB(NumberSat,NameSat.split('(')[0]+' + '+NameDtt,ConverDate(str(jData)),NumberDtt))
				else:
					self.jB.append(self.hauptListEntryMenuB(NumberSat,NameSat,ConverDate(str(DateSat)),'0'))

		if not self.jB:
			self.jB.append(self.hauptListEntryMenuB(_('Server down for maintenance'),'','',''))
			self["B"].setList(self.jB)
			self.ServerOn = False
			self.MenuA()
			return
		self["B"].setList(self.jB)

	def keyOK(self):
		if not self.ServerOn:
			return
		if self.currentlist == 'A':
			self.currentlist = 'B'
			self["B"].selectionEnabled(1)
			self["A"].selectionEnabled(0)
			return
		Type,self.AutoTimer,self.Personal,NumberSat,NameSat,self.Date,NumberDtt,self.DowDate,NameInfo=Load()
		self.name = self["B"].getCurrent()[0][1]
		self.NumberSat= self["B"].getCurrent()[0][0]
		self.NumberDtt= self["B"].getCurrent()[0][3]
		self.jType = '1'
		if self.name.lower().find('dtt') != -1:
			self.jType = '0'
		try:
			nData = int(self.Date)
		except:
			nData = 0

		try:
			njData = int(self["B"].getCurrent()[0][2].replace('-',''))
		except:
			njData = 999999

		if NameSat != self.name or Type != self.jType:
			self.session.openWithCallback(self.OnDownload, MessageBox,_('\nList: %s\nDate: %s\nYour selection is ready to install,\nwant to continue ? \nThis make take a few seconds, please wait ...') % (self.name, self['B'].getCurrent()[0][2]), MessageBox.TYPE_YESNO, timeout = 20)
		elif njData > nData:
			self.session.openWithCallback(self.OnDownload, MessageBox, _('\nList: %s\nDate: %s\nYour selection is ready to install,\nwant to continue ? \nThis make take a few seconds, please wait ...') % (self.name, self['B'].getCurrent()[0][2]), MessageBox.TYPE_YESNO, timeout = 20)
		else:
			self.session.openWithCallback(self.OnDownloadForce, MessageBox, _('\nList: %s\nDate: %s\nYour selection is already installed,\nwant to continue ? \nThis make take a few seconds, please wait ...'), MessageBox.TYPE_YESNO, timeout = 20)

	def OnDownloadForce(self,conf):
		if conf:
			self.OnDownload(True,False)

	def StartSetting(self):
		iTimerClass.StopTimer()
		iTimerClass.startTimerSetting(True)

	def OnDownload(self,conf,noForce=True):
		if conf:
			if noForce:
				WriteSave(self.jType,self.AutoTimer,self.Personal,self.NumberSat,self.name,self.Date,self.NumberDtt,self.DowDate,self.name)
			self.iTimer1.start(100,True)
		else:
			WriteSave(self.jType,self.AutoTimer,self.Personal,self.NumberSat,self.name,'0',self.NumberDtt,self.DowDate,self.name)
		self.Info()

	def keyUp(self):
		self[self.currentlist].up()
		if self.currentlist == 'A':
			self.MenuB()

	def keyDown(self):
		self[self.currentlist].down()
		if self.currentlist == 'A':
			self.MenuB()

	def keyRightLeft(self):
		self["A"].selectionEnabled(0)
		self["B"].selectionEnabled(0)
		if self.currentlist == 'A':
			if not self.ServerOn:
				return
			self.currentlist = 'B'
			self["B"].selectionEnabled(1)
			self.MenuB()
		else:
			self.currentlist = 'A'
			self["A"].selectionEnabled(1)


class picons(Screen):

	screenwidth = getDesktop(0).size().width()
	if screenwidth and screenwidth == 1920:
		skin = '\n\t\t\t<screen name="picons" position="center,center" size="960,605" >\n\t\t\t\t<widget name="text" itemHeight="50" font="Regular;28" position="10,10" size="940,580" scrollbarMode="showOnDemand" transparent="1" />\n\t\t\t\t<widget name="info" position="10,540" size="940,50" font="Rale;32" valign="center" noWrap="1" backgroundColor="#333f3f3f" foregroundColor="#FFC000" shadowOffset="-2,-2" shadowColor="black" />\n\t\t\t<widget name="lab1" position="10,540" size="940,50" font="Rale;32" valign="center" noWrap="1" backgroundColor="#333f3f3f" foregroundColor="#FFC000" shadowOffset="-2,-2" shadowColor="black" />\n\t\t\t</screen>'
	else:
		skin = '\n\t\t\t<screen name="picons" position="center,center" size="560,405" >\n\t\t\t\t<widget name="text" position="10,10" size="540,280" scrollbarMode="showOnDemand" transparent="1" />\n\t\t\t\t<widget name="info" position="10,370" size="540,30" font="Rale;22" valign="center" noWrap="1" backgroundColor="#333f3f3f" foregroundColor="#FFC000" shadowOffset="-2,-2" shadowColor="black" />\n\t\t\t<widget name="lab1" position="10,370" size="540,30" font="Rale;22" valign="center" noWrap="1" backgroundColor="#333f3f3f" foregroundColor="#FFC000" shadowOffset="-2,-2" shadowColor="black" />\n\t\t\t</screen>'


	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self['text'] = MenuList([])
		self["info"] = Label()
		self['lab1'] = Label(_("It is recommended !!\nto mount the appropriate device before downloading.\nOtherwise\nPress OK to continue"))
		self.addon = "Picons"
		self.icount = 0
		self.downloading=False
		self.mount=True
		Screen.__init__(self, session)
		self['pixmap'] = Pixmap()
		self['actions'] = ActionMap([
                'OkCancelActions', 'ColorActions', 'DirectionActions'], 
                   {'ok': self.okClicked,
                    'cancel': self.close,
                    'red': self.close }, -1)
		self['Key_Red'] = Label(_('Exit'))
		self["info"].setText("Connetting to\nAddons server...please wait")
		self.timer = eTimer()
		self.timer.callback.append(self.load)
		self.timer.start(200, 3)
	def load(self):
		xurl = "http://gioppygio.net/XML/Picons.xml"
		print "xurl =", xurl
		xdest = "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Picons.xml"
		print "xdest =", xdest
		try:
			xlist = urllib.urlretrieve(xurl, xdest)
			myfile = file(r"/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Picons.xml")
			self.data = []
			self.names = []
			icount = 0
			list = []
			xmlparse = xml.dom.minidom.parse(myfile)
			self.xmlparse=xmlparse
			for plugins in xmlparse.getElementsByTagName("plugins"):
				self.names.append(plugins.getAttribute("cont").encode("utf8"))
				self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.close}, -1)        
				self.list=list
				self["info"].setText("")
				self["text"].setList(self.names)
				self.mount=True
#				self["info"].setText("It is recommended !!\nto mount the appropriate device before downloading.\nOtherwise\nPress OK to continue")
				self.downloading=True
		except:
			self.downloading=False
			self["info"].setText("Addons Download Failure,please check internet connection !")

	def setWindowTitle(self):
		self.setTitle(_("Dowanloding"))
		self.session.openWithCallback(self.callMyMsg, MessageBox, _("It is recommended !!\nto mount the appropriate device before downloading.\nOtherwise\nPress OK to continue"), MessageBox.TYPE_YESNO)
	def okClicked(self):
		selection = str(self["text"].getCurrent())
		self.session.open(SelectCountry, self.xmlparse, selection)

class SelectCountry(Screen):

	screenwidth = getDesktop(0).size().width()
	if screenwidth and screenwidth == 1920:
         skin = '\n\t\t\t<screen name="SelectCountry" position="center,center" size="960,605" >\n\t\t\t\t<widget name="countrymenu" itemHeight="50" font="Regular;28" position="10,10" size="940,580" scrollbarMode="showOnDemand" transparent="1" />\n\t\t\t\t<widget name="info" position="10,540" size="940,50" font="Rale;32" valign="center" noWrap="1" backgroundColor="#333f3f3f" foregroundColor="#FFC000" shadowOffset="-2,-2" shadowColor="black" />\n\t\t\t</screen>'
	else:
		skin = '\n\t\t\t<screen name="SelectCountry" position="center,center" size="560,405" >\n\t\t\t\t<widget name="countrymenu" position="10,10" size="540,280" scrollbarMode="showOnDemand" transparent="1" />\n\t\t\t\t<widget name="info" position="10,370" size="540,30" font="Rale;22" valign="center" noWrap="1" backgroundColor="#333f3f3f" foregroundColor="#FFC000" shadowOffset="-2,-2" shadowColor="black" />\n\t\t\t</screen>'

	def __init__(self, session, xmlparse, selection):
		Screen.__init__(self,session)
		self['pixmap'] = Pixmap()
		self["info"] = Label(_("It is recommended !!\nto mount the appropriate device before downloading.\nOtherwise\nPress OK to install."))
		self['actions'] = ActionMap(['OkCancelActions', 'ColorActions', 'DirectionActions'], 
                     {'ok': self.selCountry,
                      'cancel': self.close,
                      'red': self.close }, -1)
		self['Key_Red'] = Label(_('Exit'))
#		self["info"].setText("It is recommended !!\nto mount the appropriate device before downloading.\nOtherwise\nPress OK to install.")
		self.xmlparse = xmlparse
		self.selection = selection
		list = []
		for plugins in self.xmlparse.getElementsByTagName("plugins"):
			if str(plugins.getAttribute("cont").encode("utf8")) == self.selection:
				for plugin in plugins.getElementsByTagName("plugin"):
					list.append(plugin.getAttribute("name").encode("utf8"))
				list.sort()
		self["countrymenu"] = MenuList(list)

	def selCountry(self):
		selection_country = self["countrymenu"].getCurrent()
		for plugins in self.xmlparse.getElementsByTagName("plugins"):
			if str(plugins.getAttribute("cont").encode("utf8")) == self.selection:
				for plugin in plugins.getElementsByTagName("plugin"):  
					if plugin.getAttribute("name").encode("utf8") == selection_country:
						urlserver = str(plugin.getElementsByTagName("url")[0].childNodes[0].data)
						pluginname = plugin.getAttribute("name").encode("utf8")     
						self.prombt(urlserver,pluginname)

	def prombt(self, com,dom):
		self.com=com
		self.dom=dom
		if self.selection=="Picons":
#			self["info"].setText("It is recommended !!\nto mount the appropriate device before downloading")
			self.session.openWithCallback(self.callMyMsg, MessageBox, _("It is recommended !!\nto mount the appropriate device before downloading.\nOtherwise\nPress OK to install."), MessageBox.TYPE_YESNO)
		else:
			self.session.open(Console,_("downloading-installing: %s") % (dom), ["opkg install -force-overwrite %s" % com])

	def callMyMsg(self, result):
		if result:
			dom=self.dom
			com=self.com
			self.session.open(Console,_("downloading-installing: %s") % (dom), ["ipkg install -force-overwrite %s" % com])
	def close_session(self):
		self.close()


jsession = None
iTimerClass = GioppyGioSettings(jsession)

def SessionStart(reason, **kwargs):
	if reason == 0:
		iTimerClass.gotSession(kwargs["session"])
	jsession = kwargs["session"]


iTimerClass = GioppyGioSettings(jsession)

def AutoStart(reason, **kwargs):
	if reason == 1:
		iTimerClass.StopTimer()


def Main(session, **kwargs):
	session.open(MenuGio)


def Plugins(**kwargs):
    return [PluginDescriptor(name='GioppyGio Panel v.2.3', description='Enigma2 Channel Settings and Picons v.2.3!', icon='/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/plugin.png', where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], fnc=Main),
	    PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=SessionStart),
	    PluginDescriptor(where=PluginDescriptor.WHERE_AUTOSTART, fnc=AutoStart)]
global giopath ## Warning: Unused global

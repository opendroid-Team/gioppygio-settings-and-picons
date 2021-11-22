#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import print_function
from Components.Label import Label
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.Sources.List import List
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Screens.Console import Console
from Components.Pixmap import Pixmap
from Plugins.Plugin import PluginDescriptor
from Components.PluginList import PluginList
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.MultiContent import MultiContentEntryText
from enigma import *
from Components.ActionMap import NumberActionMap
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
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, fileExists, pathExists, createDir, SCOPE_PLUGINS, SCOPE_SKINS, SCOPE_GUISKIN
from xml.dom import Node, minidom
from twisted.web.client import getPage, downloadPage
from Components.Button import Button
from sys import version_info
from six.moves.urllib.parse import urlparse, urlunparse
from six.moves.urllib.request import Request, urlopen
from six.moves.urllib.parse import urlencode
from six.moves import urllib
import six
from Components.Task import Task, Job, job_manager as JobManager, Condition
from Screens.TaskView import JobView
from ServiceReference import ServiceReference
from os import listdir
from twisted.web.client import downloadPage, getPage
from enigma import *
import sys
import os
import socket
from .Moduli.Setting import *
from .Moduli.Config import *
from .Moduli.Select import *
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
plugin_path = '/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/'
from enigma import addFont
global giopath
global Index
global ipk
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
                self['key_red'] = Label(_('Exit'))
                self['Key_green'] = Label(_('Installed list:'))
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
                Type, AutoTimer, Personal, NumberSat, NameSat, Date, NumberDtt, DowDate, NameInfo = Load()
                if str(Personal).strip() == '0':
                        self['Key_Personal'].setText(_("Favorites: Yes"))
                        Personal = '1'
                        self.session.open(MenuSelect)
                else:
                        self['Key_Personal'].setText(_("Favorites: No"))
                        Personal = '0'
                WriteSave(Type, AutoTimer, Personal, NumberSat, NameSat, Date, NumberDtt, DowDate, NameInfo)

        def ReturnSelect(self):
                Type, AutoTimer, Personal, NumberSat, NameSat, Date, NumberDtt, DowDate, NameInfo= Load()
                if not os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Moduli/Settings/Select' ) or os.path.getsize('/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Moduli/Settings/Select' ) < 20:
                        self['Key_Personal'].setText(_("Favorites: No"))
                        WriteSave(Type, AutoTimer,'0' , NumberSat, NameSat, Date,NumberDtt, DowDate, NameInfo)

        def Auto(self):
                if self.StopAutoWrite:
                        return
                self.StopAutoWrite = True
                iTimerClass.StopTimer()
                self.Type, AutoTimer, self.Personal, self.NumberSat, self.NameSat, self.Date, self.NumberDtt, self.DowDate, self.NameInfo= Load()
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
                WriteSave(self.Type, self.jAutoTimer, self.Personal, self.NumberSat, self.NameSat, self.Date, self.NumberDtt, self.DowDate, self.NameInfo)

        def Info(self):
                Type, AutoTimer, Personal, NumberSat, NameSat, Date, NumberDtt, DowDate, NameInfo = Load()
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
                        newDowDate = _("Last Update:") + DowDate
                self['Key_Personal'].setText(_("Favorites:")+jPersonal)
                self['autotimer'].setText(_("Auto Update:")+TypeTimer)
                self['namesat'].setText(NameInfo + newdate)
                self['dateDow'].setText(newDowDate)

        def hauptListEntryMenuA(self, name, type):
                res = [(name, type)]
                if getDesktop(0).size().width() == 1920:
                        res.append(MultiContentEntryText(pos=(60, 7), size=(230, 45), font=0, text=name, flags=RT_HALIGN_LEFT))
                        res.append(MultiContentEntryText(pos=(0, 0), size=(8, 0), font=0, text=type, flags=RT_HALIGN_LEFT))
                else:
                        res.append(MultiContentEntryText(pos=(10, 7), size=(200, 45), font=0, text=name, flags=RT_HALIGN_LEFT))
                        res.append(MultiContentEntryText(pos=(0, 0), size=(8, 0), font=0, text=type, flags=RT_HALIGN_LEFT))
                return res

        def hauptListEntryMenuB(self, NumberSat, Name, jData, NumberDtt):
                res = [(NumberSat, Name, jData, NumberDtt)]
                if getDesktop(0).size().width() == 1920:
                        res.append(MultiContentEntryText(pos=(10, 5), size=(750, 35), font=0, text=Name, flags=RT_HALIGN_LEFT))
                        res.append(MultiContentEntryText(pos=(0, 0), size=(0, 0), font=0, text=jData, flags=RT_HALIGN_LEFT))
                        res.append(MultiContentEntryText(pos=(10, 5), size=(460, 35), font=0, text=Name, flags=RT_HALIGN_LEFT))
                        res.append(MultiContentEntryText(pos=(500, 5), size=(120, 35), font=0, text=jData, flags=RT_HALIGN_LEFT))
                        res.append(MultiContentEntryText(pos=(0, 0), size=(0, 0), font=0, text=NumberDtt, flags=RT_HALIGN_LEFT))
                        res.append(MultiContentEntryText(pos=(0, 0), size=(0, 0), font=0, text=NumberSat, flags=RT_HALIGN_LEFT))
                else:
                        res.append(MultiContentEntryText(pos=(10, 5), size=(850, 45), font=0, text=Name, flags=RT_HALIGN_LEFT))
                        res.append(MultiContentEntryText(pos=(0, 0), size=(0, 0), font=0, text=jData, flags=RT_HALIGN_LEFT))
                        res.append(MultiContentEntryText(pos=(10, 5), size=(650, 45), font=0, text=Name, flags=RT_HALIGN_LEFT))
                        res.append(MultiContentEntryText(pos=(360, 5), size=(200, 45), font=0, text=jData, flags=RT_HALIGN_LEFT))
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
                        self.jB.append(self.hauptListEntryMenuB('', _(''), "xx", "xx"))
                        self.jB.append(self.hauptListEntryMenuB('', _(''), "xx", "xx"))
                        self.jB.append(self.hauptListEntryMenuB('', _(''), "xx", "xx"))
                        self.jB.append(self.hauptListEntryMenuB('', _(''), "xx", "xx"))
                        self.jB.append(self.hauptListEntryMenuB('', _(''), "xx", "xx"))
                        self['B'].setList(self.jB)
                        return
                for NumberSat, NameSat, LinkSat, DateSat, NumberDtt, NameDtt, LinkDtt, DateDtt in self.List:
                        if NameSat.lower().find(self["A"].getCurrent()[0][1]) != -1:
                                if str(NameDtt) != '0':
                                        jData = str(DateSat)
                                        if int(DateDtt) > int(DateSat):
                                                jData = str(DateDtt)
                                        self.jB.append(self.hauptListEntryMenuB(NumberSat, NameSat.split('(')[0]+' + '+NameDtt, ConverDate(str(jData)), NumberDtt))
                                else:
                                        self.jB.append(self.hauptListEntryMenuB(NumberSat, NameSat, ConverDate(str(DateSat)), '0'))

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
                Type, self.AutoTimer, self.Personal, NumberSat, NameSat, self.Date, NumberDtt, self.DowDate, NameInfo = Load()
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
                        self.session.openWithCallback(self.OnDownload, MessageBox,_ ("The new configurations are saved\nSetting: %s\nDate: %s\nThe choice is different from the previous\nDo you want to proceed with the manual upgrade?") % (self.name, self["B"].getCurrent()[0][2]), MessageBox.TYPE_YESNO, timeout = 20)
                elif njData > nData:
                        self.session.openWithCallback(self.OnDownload, MessageBox, _("The new configurations are saved\nSetting: %s\nDate: %s \n The new setting has a more recent date\nDo you want to proceed with the manual upgrade?") % (self.name, self["B"].getCurrent()[0][2]), MessageBox.TYPE_YESNO, timeout = 20)
                else:
                        self.session.openWithCallback(self.OnDownloadForce, MessageBox, _("Setting already updated, you want to upgrade anyway?"), MessageBox.TYPE_YESNO, timeout = 20)

        def OnDownloadForce(self,conf):
                if conf:
                        self.OnDownload(True,False)

        def StartSetting(self):
                iTimerClass.StopTimer()
                iTimerClass.startTimerSetting(True)

        def OnDownload(self,conf,noForce=True):
                if conf:
                        if noForce:
                                WriteSave(self.jType, self.AutoTimer, self.Personal, self.NumberSat, self.name, self.Date, self.NumberDtt, self.DowDate, self.name)
                        self.iTimer1.start(100,True)
                else:
                        WriteSave(self.jType, self.AutoTimer, self.Personal, self.NumberSat, self.name, '0', self.NumberDtt, self.DowDate, self.name)
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

class RSList(MenuList):
        def __init__(self, list):
                MenuList.__init__(self, list, True, eListboxPythonMultiContent)
                if getDesktop(0).size().width() == 1920:
                        try:
                                font = skin.fonts.get("RSList", ("Regular", 32, 50))
                                self.l.setFont(0, gFont(font[0], font[1]))
                                self.l.setItemHeight(font[2])
                        except:
                                self.l.setFont(0, gFont("Regular", 32))
                                self.l.setItemHeight(50)
                else:
                        try:
                                font = skin.fonts.get("RSList", ("Regular", 19, 50))
                                self.l.setFont(0, gFont(font[0], font[1]))
                                self.l.setItemHeight(font[2])
                        except:
                                self.l.setFont(0, gFont("Regular", 19))
                                self.l.setItemHeight(50)

def RSListEntry(download, state):
        res = [(download)]
        if getDesktop(0).size().width() == 1920:
                try:
                        x, y, w, h, x1, y1, w1, h1 = skin.parameters.get("RSList",(60, 5, 1920, 38, 5, 0, 38, 38))
                except:
                        x = 50
                        y = 5
                        w = 950
                        h = 38
                        x1 = 8
                        y1 = 10
                        w1 = 38
                        h1 = 38
        else:
                try:
                        x, y, w, h, x1, y1, w1, h1 = skin.parameters.get("RSList",(40, 0, 1280, 35, 5, 0, 38, 38))
                except:
                        x = 50
                        y = 0
                        w = 820
                        h = 38
                        x1 = 8
                        y1 = 0
                        w1 = 38
                        h1 = 38
        res.append(MultiContentEntryText(pos=(x, y), size=(w, h), font=0, text=download))
        if getDesktop(0).size().width() == 1920:
                if state == 0:
                        res.append(MultiContentEntryPixmapAlphaTest(pos=(x1, y1), size=(w1, h1), png=LoadPixmap(cached=True, desktop=getDesktop(0), path=resolveFilename(SCOPE_GUISKIN, "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/lock_on.png"))))
                else:
                        res.append(MultiContentEntryPixmapAlphaTest(pos=(x1, y1), size=(w1, h1), png=LoadPixmap(cached=True, desktop=getDesktop(0), path=resolveFilename(SCOPE_GUISKIN, "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/lock_off.png"))))
        else:
                if state == 0:
                        res.append(MultiContentEntryPixmapAlphaTest(pos=(x1, y1), size=(w1, h1), png=LoadPixmap(cached=True, desktop=getDesktop(0), path=resolveFilename(SCOPE_GUISKIN, "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/menu_on.png"))))
                else:
                        res.append(MultiContentEntryPixmapAlphaTest(pos=(x1, y1), size=(w1, h1), png=LoadPixmap(cached=True, desktop=getDesktop(0), path=resolveFilename(SCOPE_GUISKIN, "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/menu_off.png"))))
        return res

##############################################################################
class picons(Screen):
        skin = """
		<screen name="picons" position="center,60" size="800,635" title="OPENDROID Addons Manager" >
		<widget name="list" position="80,100" size="710,350" zPosition="2" scrollbarMode="showOnDemand" transparent="1"/>
		<widget name="key_red" position="135,600" zPosition="1" size="180,45" font="Regular;18" foregroundColor="red" backgroundColor="red" transparent="1" />
		<widget name="key_green" position="400,600" zPosition="1" size="100,45" font="Regular;18" foregroundColor="green" backgroundColor="green" transparent="1" />
		<widget name="key_yellow" position="675,600" zPosition="1" size="180,45" font="Regular;18" foregroundColor="yellow" backgroundColor="yellow" transparent="1" />
		</screen>"""
        def __init__(self, session):
                Screen.__init__(self, session)
                self.list=[]
                self.entrylist = []  #List reset
                if getDesktop(0).size().width() == 1920:
                        self.entrylist.append((_("Picons-4.8-EST-HDD-White&Black"), "4.8-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                        self.entrylist.append((_("Picons-4.8-EST-USB-White&Black"), "4.8-EST-USB", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-USB.png"))
                        self.entrylist.append((_("Picons-7.0-EST-HDD-White&Black"), "7.0-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                        self.entrylist.append((_("Picons-7.0-EST-USB-White&Black"), "7.0-EST-USB", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-USB.png"))
                        self.entrylist.append((_("Picons-9.0-EST-HDD-White&Black"), "9.0-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                        self.entrylist.append((_("Picons-9.0-EST-USB-White&Black"), "9.0-EST-USB", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-USB.png"))
                        self.entrylist.append((_("Picons-13.0-EST-HDD-White&Black"), "13.0-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                        self.entrylist.append((_("Picons-13.0-EST-USB-White&Black"), "13.0-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-USB.png"))
                        self.entrylist.append((_("Picons-16.0-EST-HDD-White&Black"), "16.0-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                        self.entrylist.append((_("Picons-16.0-EST-USB-White&Black"), "16.0-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-USB.png"))
                        self.entrylist.append((_("Picons-19.2-EST-HDD-White&Black"), "19.2-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                        self.entrylist.append((_("Picons-19.2-EST-USB-White&Black"), "19.2-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-USB.png"))
                        self.entrylist.append((_("Picons-23.5-EST-HDD-White&Black"), "23.5-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                        self.entrylist.append((_("Picons-23.5-EST-USB-White&Black"), "23.5-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-USB.png"))
                        self.entrylist.append((_("Picons-26.0-EST-HDD-White&Black"), "26.0-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                        self.entrylist.append((_("Picons-26.0-EST-USB-White&Black"), "26.0-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-USB.png"))
                        self.entrylist.append((_("Picons-28.2-EST-HDD-White&Black"), "28.2-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                        self.entrylist.append((_("Picons-28.2-EST-USB-White&Black"), "28.2-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-USB.png"))
                        self.entrylist.append((_("Picons-31.5-EST-HDD-White&Black"), "31.5-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                        self.entrylist.append((_("Picons-31.5-EST-USB-White&Black"), "31.5-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-USB.png"))
                        self.entrylist.append((_("Picons-39-EST-HDD-White&Black"), "39-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                        self.entrylist.append((_("Picons-39-EST-USB-White&Black"), "39-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-USB.png"))
                        self.entrylist.append((_("Picons-42.0-EST-HDD-White&Black"), "42.0-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                        self.entrylist.append((_("Picons-42.0-EST-USB-White&Black"), "42.0-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-USB.png"))
                        self.entrylist.append((_("Picons-0.8-OVEST-HDD-White&Black"), "0.8-OVEST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                        self.entrylist.append((_("Picons-0.8-OVEST-USB-White&Black"), "0.8-OVEST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-USB.png"))
                        self.entrylist.append((_("Picons-5.0-OVEST-HDD-White&Black"), "5.0-OVEST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                        self.entrylist.append((_("Picons-5.0-OVEST-USB-White&Black"), "5.0-OVEST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-USB.png"))
                        self.entrylist.append((_("Picons-7.0-OVEST-HDD-White&Black"), "7.0-OVEST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                        self.entrylist.append((_("Picons-7.0-OVEST-USB-White&Black"), "7.0-OVEST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-USB.png"))
                        self.entrylist.append((_("Picons-30.0-OVEST-HDD-White&Black"), "30.0-OVEST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                        self.entrylist.append((_("Picons-30.0-OVEST-USB-White&Black"), "30.0-OVEST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-USB.png"))
                        self.entrylist.append((_("Picons-DTT-HDD-USB-White&Black"), "DTT-HDD-USB", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/Picons-HDD.png"))
                else:
                        self.entrylist.append((_("Picons-4.8-EST-HDD-White&Black"), "4.8-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                        self.entrylist.append((_("Picons-4.8-EST-USB-White&Black"), "4.8-EST-USB", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-usb.png"))
                        self.entrylist.append((_("Picons-7.0-EST-HDD-White&Black"), "7.0-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                        self.entrylist.append((_("Picons-7.0-EST-USB-White&Black"), "7.0-EST-USB", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-usb.png"))
                        self.entrylist.append((_("Picons-9.0-EST-HDD-White&Black"), "9.0-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                        self.entrylist.append((_("Picons-9.0-EST-USB-White&Black"), "9.0-EST-USB", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-usb.png"))
                        self.entrylist.append((_("Picons-13.0-EST-HDD-White&Black"), "13.0-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                        self.entrylist.append((_("Picons-13.0-EST-USB-White&Black"), "13.0-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-usb.png"))
                        self.entrylist.append((_("Picons-16.0-EST-HDD-White&Black"), "16.0-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                        self.entrylist.append((_("Picons-16.0-EST-USB-White&Black"), "16.0-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-usb.png"))
                        self.entrylist.append((_("Picons-19.2-EST-HDD-White&Black"), "19.2-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                        self.entrylist.append((_("Picons-19.2-EST-USB-White&Black"), "19.2-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-usb.png"))
                        self.entrylist.append((_("Picons-23.5-EST-HDD-White&Black"), "23.5-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                        self.entrylist.append((_("Picons-23.5-EST-USB-White&Black"), "23.5-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-usb.png"))
                        self.entrylist.append((_("Picons-26.0-EST-HDD-White&Black"), "26.0-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                        self.entrylist.append((_("Picons-26.0-EST-USB-White&Black"), "26.0-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-usb.png"))
                        self.entrylist.append((_("Picons-28.2-EST-HDD-White&Black"), "28.2-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                        self.entrylist.append((_("Picons-28.2-EST-USB-White&Black"), "28.2-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-usb.png"))
                        self.entrylist.append((_("Picons-31.5-EST-HDD-White&Black"), "31.5-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                        self.entrylist.append((_("Picons-31.5-EST-USB-White&Black"), "31.5-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-usb.png"))
                        self.entrylist.append((_("Picons-39-EST-HDD-White&Black"), "39-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                        self.entrylist.append((_("Picons-39-EST-USB-White&Black"), "39-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-usb.png"))
                        self.entrylist.append((_("Picons-42.0-EST-HDD-White&Black"), "42.0-EST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                        self.entrylist.append((_("Picons-42.0-EST-USB-White&Black"), "42.0-EST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-usb.png"))
                        self.entrylist.append((_("Picons-0.8-OVEST-HDD-White&Black"), "0.8-OVEST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                        self.entrylist.append((_("Picons-0.8-OVEST-USB-White&Black"), "0.8-OVEST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-usb.png"))
                        self.entrylist.append((_("Picons-5.0-OVEST-HDD-White&Black"), "5.0-OVEST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                        self.entrylist.append((_("Picons-5.0-OVEST-USB-White&Black"), "5.0-OVEST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-usb.png"))
                        self.entrylist.append((_("Picons-7.0-OVEST-HDD-White&Black"), "7.0-OVEST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                        self.entrylist.append((_("Picons-7.0-OVEST-USB-White&Black"), "7.0-OVEST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-usb.png"))
                        self.entrylist.append((_("Picons-30.0-OVEST-HDD-White&Black"), "30.0-OVEST-HDD", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                        self.entrylist.append((_("Picons-30.0-OVEST-USB-White&Black"), "30.0-OVEST-USB","/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/default/Picons-usb.png"))
                        self.entrylist.append((_("Picons-DTT-HDD-USB-White&Black"), "DTT-HDD-USB", "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/default/Picons-hd.png"))
                self['list'] = PluginList(self.list)
                self["key_red"] = Label(_("Exit"))
#		self["key_green"] = Label(_("Remove"))
                self["key_yellow"] = Label(_("Restart E2"))
                self['lab1'] = Label(_("It is recommended !!\nmount the appropriate device \nbefore downloading.\nOtherwise\nPress OK to continue"))
                self['actions'] = ActionMap(['WizardActions','ColorActions'],
		{
			'ok': self.KeyOk,
                        "red": self.close,
                        'back': self.close,
#			'green': self.Remove,
                        'yellow' : self.RestartE2,
		})
                self.onLayoutFinish.append(self.updateList)

#	def Remove(self):
#		self.session.open(AddonsRemove)
        def RestartE2(self):
                msg="Do you want Restart GUI now ?"
                self.session.openWithCallback(self.Finish, MessageBox, msg, MessageBox.TYPE_YESNO)
        def Finish(self, answer):
                if answer is True:
                        self.session.open(TryQuitMainloop, 3)
                else:
                        self.close()
        def KeyOk(self):
                selection = self["list"].getCurrent()[0][1]
                print(selection)
                if (selection == "5.0-OVEST-HDD"):
                        addons = 'Picons-5.0-OVEST-HDD'
                        self.title = 'Picons GioppyGio Downloader 5.0-OVEST-HDD'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "5.0-OVEST-USB"):
                        addons = 'Picons-5.0-OVEST-USB'
                        self.title = 'Picons GioppyGio Downloader 5.0-OVEST-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "7.0-OVEST-HDD"):
                        addons = 'Picons-7.0-OVEST-HDD'
                        self.title = 'Picons GioppyGio Downloader 7.0-OVEST-HDD'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "7.0-OVEST-USB"):
                        addons = 'Picons-7.0-OVEST-USB'
                        self.title = 'Picons GioppyGio Downloader 7.0-OVEST-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "0.8-OVEST-HDD"):
                        addons = 'Picons-0.8-OVEST-HDD'
                        self.title = 'Picons GioppyGio Downloader 0.8-OVEST-HDD'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "0.8-OVEST-USB"):
                        addons = 'Picons-0.8-OVEST-USB'
                        self.title = 'Picons GioppyGio Downloader 0.8-OVEST-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "4.8-EST-HDD"):
                        addons = 'Picons-4.8-EST-HDD'
                        self.title = 'Picons GioppyGio Downloader 4.8-EST-HDD'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "4.8-EST-USB"):
                        addons = 'Picons-4.8-EST-USB'
                        self.title = 'Picons GioppyGio Downloader 4.8-EST-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "39-EST-HDD"):
                        addons = 'Picons-39-EST-HDD'
                        self.title = 'Picons GioppyGio Downloader 39-EST-HDD'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "39-EST-USB"):
                        addons = 'Picons-39-EST-USB'
                        self.title = 'Picons GioppyGio Downloader 39-EST-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "23.5-EST-HDD"):
                        addons = 'Picons-23.5-EST-HDD'
                        self.title = 'Picons GioppyGio Downloader 39-EST-HDD'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "23.5-EST-USB"):
                        addons = 'Picons-23.5-EST-USB'
                        self.title = 'Picons GioppyGio Downloader 23.5-EST-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "7.0-EST-HDD"):
                        addons = 'Picons-7.0-EST-HDD'
                        self.title = 'Picons GioppyGio Downloader 7.0-EST-HDD'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "7.0-EST-USB"):
                        addons = 'Picons-7.0-EST-USB'
                        self.title = 'Picons GioppyGio Downloader 7.0-EST-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "9.0-EST-HDD"):
                        addons = 'Picons-9.0-EST-HDD'
                        self.title = 'Picons GioppyGio Downloader 9.0-EST-HDD'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "9.0-EST-USB"):
                        addons = 'Picons-9.0-EST-USB'
                        self.title = 'Picons GioppyGio Downloader 9.0-EST-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "16.0-EST-HDD"):
                        addons = 'Picons-16.0-EST-HDD'
                        self.title = 'Picons GioppyGio Downloader 16.0-EST-HDD'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "16.0-EST-USB"):
                        addons = 'Picons-16.0-EST-USB'
                        self.title = 'Picons GioppyGio Downloader 16.0-EST-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "26.0-EST-HDD"):
                        addons = 'Picons-26.0-EST-HDD'
                        self.title = 'Picons GioppyGio Downloader 26.0-EST-HDD'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "26.0-EST-USB"):
                        addons = 'Picons-26.0-EST-USB'
                        self.title = 'Picons GioppyGio Downloader 26.0-EST-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "28.2-EST-HDD"):
                        addons = 'Picons-28.2-EST-HDD'
                        self.title = 'Picons GioppyGio Downloader 28.2-EST-HDD'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "28.2-EST-USB"):
                        addons = 'Picons-28.2-EST-USB'
                        self.title = 'Picons GioppyGio Downloader 28.2-EST-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "13.0-EST-HDD"):
                        addons = 'Picons-13.0-EST-HDD'
                        self.title = 'Picons GioppyGio Downloader 13.0-EST-HDD'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "13.0-EST-USB"):
                        addons = 'Picons-13.0-EST-USB'
                        self.title = 'Picons GioppyGio Downloader 13.0-EST-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "19.2-EST-HDD"):
                        addons = 'Picons-19.2-EST-HDD'
                        self.title = 'Picons GioppyGio Downloader 19.2-EST-HDD'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "19.2-EST-USB"):
                        addons = 'Picons-19.2-EST-USB'
                        self.title = 'Picons GioppyGio Downloader 19.2-EST-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "31.5-EST-HDD"):
                        addons = 'Picons-31.5-EST-HDD'
                        self.title = 'Picons GioppyGio Downloader 31.5-EST-HDD'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "31.5-EST-USB"):
                        addons = 'Picons-31.5-EST-USB'
                        self.title = 'Picons GioppyGio Downloader 31.5-EST-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "42.0-EST-HDD"):
                        addons = 'Picons-42.0-EST-HDD'
                        self.title = 'Picons GioppyGio Downloader 42.0-EST-HDD'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "42.0-EST-USB"):
                        addons = 'Picons-42.0-EST-USB'
                        self.title = 'Picons GioppyGio Downloader 42.0-EST-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "DTT-HDD-USB"):
                        addons = 'Picons-DTT-HDD-USB'
                        self.title = 'Picons GioppyGio Downloader DTT-HDD-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "DTT-USB"):
                        addons = 'Picons-DTT-USB'
                        self.title = 'Picons GioppyGio Downloader DTT-USB'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "30.0-OVEST-HDD"):
                        addons = 'Picons-30.0-OVEST-HDD'
                        self.title = 'Picons GioppyGio Downloader 30.0-OVEST-HDD'
                        self.session.open(ipklist, addons, self.title)
                elif (selection == "30.0-OVEST-USB"):
                        addons = 'Picons-30.0-OVEST-USB'
                        self.title = 'Picons GioppyGio Downloader 30.0-OVEST-USB'
                        self.session.open(ipklist, addons, self.title)
                else:
                        self.messpopup("Selection error")

        def messpopup(self,msg):
                self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)

        def updateList(self):
                for i in self.entrylist:
                        res = [i]
                        res.append(MultiContentEntryText(pos=(60, 5), size=(1100, 48), font=0, text=i[0]))
                        picture=LoadPixmap(resolveFilename(SCOPE_GUISKIN, i[2]))
                        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(48, 48), png=picture))
                        self.list.append(res)
                self['list'].l.setList(self.list)

class ipklist(Screen):
        skin = """
		<screen position="center,center" size="800,500" title=" " >
			<widget name="text" position="100,20" size="200,30" font="Regular;20" halign="left" />
			<ePixmap position="300,25"   zPosition="2" size="140,40" pixmap="skin_default/buttons/button_red.png" transparent="1" alphatest="on" />
			<widget name="list" position="50,80" size="730,300" scrollbarMode="showOnDemand" />

			<ePixmap name="red"    position="0,460"   zPosition="2" size="140,40" pixmap="skin_default/buttons/button_red.png" transparent="1" alphatest="on" />
			<ePixmap name="green"  position="140,460" zPosition="2" size="140,40" pixmap="skin_default/buttons/button_green.png" transparent="1" alphatest="on" />

			<widget name="key_red" position="0,450" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> 
			<widget name="key_green" position="140,450" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> 

			<eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" />
			<widget name="info" position="100,230" zPosition="4" size="300,25" font="Regular;18" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />
		</screen>"""

        def __init__(self, session, addons, title):
                self.skin = ipklist.skin
                Screen.__init__(self, session)
                self.list = []
                self["text"] = Label()
                self["list"] = List(self.list)
                self["list"] = RSList([])
                self['lab1'] = Label(_("It is recommended !!\nmount the appropriate device \nbefore downloading.\nOtherwise\nPress OK to continue"))
                self["info"] = Label()
                self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
		{
                        "ok": self.okClicked,
                        "back": self.close,
                        "red": self.close,
                        "green": self.okClicked,
                        }, -1)
                self["key_red"] = Button(_("Cancel"))
                self["key_green"] = Button(_("OK"))
                self.mytitle = title
                self.addon = addons
                self["title"] = Button(title)
                self.icount = 0
                self.names = []
                self.onLayoutFinish.append(self.openTest)

        def openTest(self):
                self["info"].setText("Downloading list...")
                testno = 1
                xurl = 'https://gioppygio.it/addons/picons/' + self.addon + '/list'
                print("xurl =", xurl)
                getPage(six.ensure_binary(xurl)).addCallback(self.gotPage).addErrback(self.getfeedError)

        def gotPage(self, html):
                html = six.ensure_str(html)
                self.data = []
                icount = 0
                self.data = html.splitlines()
                list = []
                for line in self.data:
                        ipkname = self.data[icount]
                        print("gotPage icount, ipk name =", icount, ipkname)
                        remname = ipkname
                        state = self.getstate(ipkname)
                        print("gotPage state, remname = ", state, remname)
                        list.append(RSListEntry(remname, state))
                        icount = icount+1
                        self["list"].setList(list)
                        print ('self["list"] A =', self["list"])
                        self["info"].setText("")

        def getfeedError(self, error=""):
                print(str(error))
                self["resulttext"].setText(_("Invalid response from server. Please report: %s") % str(error))

        def getstate(self, ipkname):
                item = "/etc/ipkinst/" + ipkname
                if os.path.exists(item):
                        state = 1
                        return state
                else:
                        state = 0
                        return state

        def okClicked(self):
                print("Here in okClicked A")
                sel = self["list"].getSelectionIndex()
                ipk = self.data[sel]
                addon = self.addon
                ipkinst = Getipk(self.session, ipk, addon)
                ipkinst.openTest()

        def keyLeft(self):
                self["text"].left()

        def keyRight(self):
                self["text"].right()

        def keyNumberGlobal(self, number):
                print("pressed", number)
                self["text"].number(number)

class Getipk(Screen):
        skin = """
		<screen position="center,center" size="800,500" title="Install IPK" >
			<!--widget name="text" position="0,0" size="550,25" font="Regular;20" /-->
			<widget name="list" position="10,20" size="750,350" scrollbarMode="showOnDemand" />
			<!--widget name="pixmap" position="200,0" size="190,250" /-->
			<eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" />
			<widget name="info" position="50,50" zPosition="4" size="500,400" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="left" valign="top" />
			<ePixmap name="red"    position="0,450"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
			<ePixmap name="green"  position="140,450" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
			<ePixmap name="yellow" position="280,450" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" /> 
			<!--ePixmap name="blue"   position="420,450" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" /--> 
			<widget name="key_red" position="0,450" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> 
			<widget name="key_green" position="140,450" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> 
			<!--widget name="key_yellow" position="280,450" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />
			<widget name="key_blue" position="420,450" size="140,50" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /-->
		</screen>"""

        def __init__(self, session, ipk, addon):
                Screen.__init__(self, session)
                self.skin = Getipk.skin
                title = "Install IPK"
                self.setTitle(title)
                self["list"] = MenuList([])
                self["info"] = Label()
                self["key_red"] = Button(_("Exit"))
                self["key_green"] = Button(_("Install IPK"))
                self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
		{
                        "red": self.close,
                        "green": self.okClicked,
                        "yellow": self.install,
                        "cancel": self.cancel,
                        "ok": self.close
                        }, -2)
                print("Getipk : ipk =", ipk)
                self.icount = 0
                self.ipk = ipk
                self.addon = addon
                self.onLayoutFinish.append(self.openTest)
                txt = "You have selected\n\n" + ipk + "\n\n\nPlease press Download"
                self["info"].setText(txt)
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                self.onLayoutFinish.append(self.openTest)

        def openTest(self):
                if not os.path.exists("/etc/ipkinst"):
                        cmd = "mkdir -p /etc/ipkinst"
                        os.system(cmd)
                xurl1 = 'https://gioppygio.it/addons/picons/' + self.addon + '/'
                print("xurl1 =", xurl1)
                xurl2 = xurl1 + self.ipk
                print("xurl2 =", xurl2)
                xdest = "/tmp/" + self.ipk
                print("xdest =", xdest)
                self.cmd1 = 'wget -O "' + xdest + '" "' + xurl2 + '"'
                self.cmd2 = "opkg install --force-overwrite /tmp/" + self.ipk
                self.cmd3 = "touch /etc/ipkinst/" + self.ipk + " &"
                self.okClicked()

        def okClicked(self):
                plug = self.ipk
                title = _("Installing addon %s" %(plug))
                cmd = self.cmd1 + " && " + self.cmd2 + " && " + self.cmd3
                self.session.open(Console,_(title),[cmd])

        def LastJobView(self):
                currentjob = None
                for job in JobManager.getPendingJobs():
                        currentjob = job
                if currentjob is not None:
                        self.session.open(JobView, currentjob)

        def install(self):
                cmd = "opkg install --force-overwrite /tmp/" + self.ipk + ">/tmp/ipk.log"
                print("cmd =", cmd)
                title = _("Installing addon %s" % (plug))
                self.session.open(Console,_(title), [cmd])
                self.endinstall()

        def viewLog(self):
                self["info"].setText("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n       Press Exit to continue...")
                if os.path.isfile("/tmp/ipk.log")is not True :
                        cmd = "touch /tmp/ipk.log"
                        os.system(cmd)
                else:
                        myfile = file(r"/tmp/ipk.log")
                        icount = 0
                        data = []
                        for line in myfile.readlines():
                                data.append(icount)
                                print(line)
                                num = len(line)
                                data[icount] = (line[:-1])
                                print(data[icount])
                                icount = icount + 1
                        self["list"].setList(data)
                        self.endinstall()

        def endinstall(self):
                path = "/tmp"
                tmplist = []
                ipkname = 0
                tmplist = os.listdir(path)
                print("files in /tmp", tmplist)
                icount = 0
                for name in tmplist:
                        nipk = tmplist[icount]
                        if (nipk[-3:] == "ipk"):
                                ipkname = nipk
                        icount = icount+1
                if ipkname != 0:
                        print("endinstall ipk name =", ipkname)
                        ipos = ipkname.find("_")
                        remname = ipkname[:ipos]
                        print("endinstall remname =", remname)
                        f = open('/etc/ipklist_installed', 'a')
                        f1 = remname + "\n"
                        f.write(f1)
                        cmd = "rm /tmp/*.ipk"
                        os.system(cmd)

        def cancel(self):
                self.close()

        def keyLeft(self):
                self["text"].left()

        def keyRight(self):
                self["text"].right()

        def keyNumberGlobal(self, number):
                print("pressed", number)
                self["text"].number(number)

class downloadJob(Job):
        def __init__(self, toolbox, cmdline, filename, filetitle):
                Job.__init__(self, _("Downloading"))
                self.toolbox = toolbox
                self.retrycount = 0
                downloadTask(self, cmdline, filename, filetitle)

        def retry(self):
                assert self.status == self.FAILED
                self.retrycount += 1
                self.restart()

class downloadTask(Task):
        ERROR_CORRUPT_FILE, ERROR_RTMP_ReadPacket, ERROR_SEGFAULT, ERROR_SERVER, ERROR_UNKNOWN = range(5)
        def __init__(self, job, cmdline, filename, filetitle):
                Task.__init__(self, job, filetitle)
                self.setCmdline(cmdline)
                self.filename = filename
                self.toolbox = job.toolbox
                self.error = None
                self.lasterrormsg = None

        def processOutput(self, data):
                try:
                        data = six.ensure_str(data)
                        if data.endswith('%)'):
                                startpos = data.rfind("sec (")+5
                                if startpos and startpos != -1:
                                        self.progress = int(float(data[startpos:-4]))
                        elif data.find('%') != -1:
                                tmpvalue = data[:data.find("%")]
                                tmpvalue = tmpvalue[tmpvalue.rfind(" "):].strip()
                                tmpvalue = tmpvalue[tmpvalue.rfind("(")+1:].strip()
                                self.progress = int(float(tmpvalue))
                        else:
                                Task.processOutput(self, data)
                except (IOError, OSError) as errormsg:
                        print("Error processOutput: " + str(errormsg))
                        Task.processOutput(self, data)

        def processOutputLine(self, line):
                self.error = self.ERROR_SERVER

        def afterRun(self):
                pass

class downloadTaskPostcondition(Condition):
        RECOVERABLE = True
        def check(self, task):
                if task.returncode == 0 or task.error is None:
                        return True
                else:
                        return False

        def getErrorMessage(self, task):
                return {
                        task.ERROR_CORRUPT_FILE: _("Video Download Failed!Corrupted Download File:%s" % task.lasterrormsg),
                        task.ERROR_RTMP_ReadPacket: _("Video Download Failed!Could not read RTMP-Packet:%s" % task.lasterrormsg),
                        task.ERROR_SEGFAULT: _("Video Download Failed!Segmentation fault:%s" % task.lasterrormsg),
                        task.ERROR_SERVER: _("Download Failed!-Server error:"),
                        task.ERROR_UNKNOWN: _("Download Failed!Unknown Error:%s" % task.lasterrormsg)
                        }[task.error]



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
        return  [PluginDescriptor(name='GioppyGio', description='Enigma2 Channel Settings and Picons!', icon='/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Panel/plugin.png', where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], fnc=Main),
                 PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=SessionStart),
                 PluginDescriptor(where=PluginDescriptor.WHERE_AUTOSTART, fnc=AutoStart)]
        global giopath

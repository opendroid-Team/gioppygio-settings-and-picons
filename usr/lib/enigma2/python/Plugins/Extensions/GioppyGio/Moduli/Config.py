#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from random import choice
import re
import os
import xml.etree.cElementTree
import sys
from enigma import *
from .Setting import *
from urllib.request import urlopen, Request
import six

def OnclearMem():
	os.system('sync')
	os.system('echo 3 > /proc/sys/vm/drop_caches')

Directory = os.path.dirname(sys.modules[__name__].__file__)
if not os.path.exists(Directory + '/Settings'):
	os.system('mkdir  ' + Directory + '/GioppyGio')
if not os.path.exists(Directory + '/Settings/Temp'):
	os.system('mkdir  ' + Directory + '/Settings/Temp')
if os.path.exists(' /usr/lib/enigma2/python/Plugins/Extensions/'):
	os.system('rm -fr /usr/lib/enigma2/python/Plugins/Extensions/')

def ConverDate(Date):
	if not Date:
		return
	day = Date[:2]
	month = Date[-6:][:2]
	year = Date[-4:]
	return day + '-' + month + '-' + year

def Downloadxml():
	try:
		req = Request('https://gioppygio.it/XML/settings.xml')
		req.add_header('User-Agent', 'Plugin GioppyGio')
		response = urlopen(req, None, 3)
		link = response.read()
		response.close()
		return link
	except:
		return
	return

def DownloadSetting():
	ListSettings = []
	try:
		mdom = xml.etree.cElementTree.parse(six.BytesIO(Downloadxml()))
		for x in mdom.getroot():
			if x.tag == 'ruleset' and x.get('name') == 'Sat':
				rootsat = x
		for x in rootsat:
			if x.tag == 'rule':
				if x.get('type') == 'Marker':
					NumberSat = str(x.get('Number'))
					NameSat = str(x.get('Name'))
					LinkSat = str(x.get('Link'))
					DateSat = str(x.get('Date'))
					ListSettings.append((NumberSat, NameSat, LinkSat, DateSat, '0', '0', '0', '0'))
	except:
		pass

	return ListSettings

def Load():
	AutoTimer = '0'
	Type = '0'
	Personal = '0'
	NameSat = Date = NumberDtt = DowDate = NameInfo = '0'
	NumberSat = '1'
	if os.path.exists(Directory + '/Settings/Date'):
		xf = open(Directory + '/Settings/Date', 'r')
		f = xf.readlines()
		xf.close()
		for line in f:
			try:
				LoadDate = line.strip()
				elements = LoadDate.split('=')
				if LoadDate.find('AutoTimer') != -1:
					AutoTimer = elements[1][1:]
				elif LoadDate.find('Type') != -1:
					Type = elements[1][1:]
				elif LoadDate.find('Personal') != -1:
					Personal = elements[1][1:]
				elif LoadDate.find('NumberSat') != -1:
					NumberSat = elements[1][1:]
				elif LoadDate.find('NameSat') != -1:
					NameSat = elements[1][1:]
				elif LoadDate.find('jDateSat') != -1:
					Date = elements[1][1:]
				elif LoadDate.find('NumberDtt') != -1:
					NumberDtt = elements[1][1:]
				elif LoadDate.find('DowDate') != -1:
					DowDate = elements[1][1:]
				elif LoadDate.find('NameInfo') != -1:
					NameInfo = elements[1][1:]
			except:
				pass
	else:
		xf = open(Directory + '/Settings/Date', 'w')
		xf.write('AutoTimer = 0\n')
		xf.write('Type = 0\n')
		xf.write('Personal = 0\n')
		xf.write('NumberSat = 1\n')
		xf.write('NameSat = Mono (13\xc2\xb0E)\n')
		xf.write('jDateSat = 0\n')
		xf.write('NumberDtt = 0\n')
		xf.write('DowDate = 0\n')
		xf.write('NameInfo = 0\n')
		xf.close()
	return (Type, AutoTimer, Personal, NumberSat, NameSat, Date, NumberDtt, DowDate, NameInfo)

def WriteSave(Type, AutoTimer, Personal, NumberSat, NameSat, Date, NumberDtt, DowDate, NameInfo):
	xf = open(Directory + '/Settings/Date', 'w')
	xf.write('AutoTimer = %s\n' % str(AutoTimer))
	xf.write('Type = %s\n' % str(Type))
	xf.write('Personal = %s\n' % str(Personal))
	xf.write('NumberSat = %s\n' % str(NumberSat))
	xf.write('NameSat = %s\n' % str(NameSat))
	xf.write('jDateSat = %s\n' % str(Date))
	xf.write('NumberDtt = %s\n' % str(NumberDtt))
	xf.write('DowDate = %s\n' % str(DowDate))
	xf.write('NameInfo = %s\n' % str(NameInfo))
	xf.close()

def Plugin():
	Vers = Link = Date = ''
	try:
		req = Request('')
		req.add_header('User-Agent', 'Plugin GioppyGio')
		response = urlopen(req, None, 3)
		link = response.read()
		response.close()
	except:
		return
	try:
		mdom = xml.etree.cElementTree.parse(six.StringIO(link))
		for x in mdom.getroot():
			if x.tag == 'ruleset' and x.get('name') == 'Plugin':
				root = x
		for x in root:
			if x.tag == 'rule':
				if x.get('type') == 'Marker':
					Vers = str(x.get('Name'))
					Link = str(x.get('Link'))
					Date = str(x.get('Date'))
		return (Vers, Link, Date)
	except:
		return
	return

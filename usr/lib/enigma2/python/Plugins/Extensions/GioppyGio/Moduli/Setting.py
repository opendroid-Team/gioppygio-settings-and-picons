from enigma import eTimer
from random import choice
import re, glob, shutil, os, urllib2, urllib, time, sys
from os import statvfs
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Label import Label
from enigma import *
from Config import *
try:
	import zipfile
except:
	pass

Version = '2.1'
Directory = os.path.dirname(sys.modules[__name__].__file__)
MinStart = int(choice(range(59)))

def TimerControl():
	now = time.localtime(time.time())
	Ora = str(now[3]).zfill(2) + ':' + str(now[4]).zfill(2) + ':' + str(now[5]).zfill(2)
	Date = str(now[2]).zfill(2) + '-' + str(now[1]).zfill(2) + '-' + str(now[0])
	return '%s ora: %s' % (Date, Ora)


def StartSavingTerrestrialChannels(lamedb, type):

	def ForceSearchBouquetTerrestrial():
		for file in sorted(glob.glob('/etc/enigma2/*.tv')):
			f = open(file, 'r').read()
			x = f.strip().lower()
			if x.find('eeee0000') != -1:
				if x.find('82000') == -1 and x.find('c0000') == -1:
					return file
					break

	def ResearchBouquetTerrestrial(search, search1):
		for file in sorted(glob.glob('/etc/enigma2/*.tv')):
			f = open(file, 'r').read()
			x = f.strip().lower()
			x1 = f.strip()
			if x1.find('#NAME') != -1:
				if x.lower().find(search.lower()) != -1 or x.lower().find(search1.lower()) != -1:
					if x.find('eeee0000') != -1:
						return file
						break

	def SaveTrasponderService(lamedb):
		TrasponderListOldLamedb = open(Directory + '/Settings/Temp/TrasponderListOldLamedb', 'w')
		ServiceListOldLamedb = open(Directory + '/Settings/Temp/ServiceListOldLamedb', 'w')
		Trasponder = False
		inTransponder = False
		inService = False
		try:
			LamedbFile = open(lamedb)
			while 1:
				line = LamedbFile.readline()
				if not line:
					break
				if not (inTransponder or inService):
					if line.find('transponders') == 0:
						inTransponder = True
					if line.find('services') == 0:
						inService = True
				if line.find('end') == 0:
					inTransponder = False
					inService = False
				line = line.lower()
				if line.find('eeee0000') != -1:
					Trasponder = True
					if inTransponder:
						TrasponderListOldLamedb.write(line)
						line = LamedbFile.readline()
						TrasponderListOldLamedb.write(line)
						line = LamedbFile.readline()
						TrasponderListOldLamedb.write(line)
					if inService:
						tmp = line.split(':')
						ServiceListOldLamedb.write(tmp[0] + ':' + tmp[1] + ':' + tmp[2] + ':' + tmp[3] + ':' + tmp[4] + ':0\n')
						line = LamedbFile.readline()
						ServiceListOldLamedb.write(line)
						line = LamedbFile.readline()
						ServiceListOldLamedb.write(line)

			TrasponderListOldLamedb.close()
			ServiceListOldLamedb.close()
			if not Trasponder:
				os.system('rm -fr ' + Directory + '/Settings/Temp/TrasponderListOldLamedb')
				os.system('rm -fr ' + Directory + '/Settings/Temp/ServiceListOldLamedb')
		except:
			pass

		return Trasponder

	def CreateBouquetForce():
		WritingBouquetTemporary = open(Directory + '/Settings/Temp/TerrestrialChannelListArchive', 'w')
		WritingBouquetTemporary.write('#NAME terrestre\n')
		ReadingTempServicelist = open(Directory + '/Settings/Temp/ServiceListOldLamedb').readlines()
		for jx in ReadingTempServicelist:
			if jx.find('eeee') != -1:
				String = jx.split(':')
				WritingBouquetTemporary.write('#SERVICE 1:0:%s:%s:%s:%s:%s:0:0:0:\n' % (hex(int(String[4]))[2:], String[0], String[2], String[3], String[1]))

		WritingBouquetTemporary.close()

	def SaveBouquetTerrestrial(istype):
		if istype:
			try:
				shutil.copyfile(Directory + '/Settings/Temp/enigma2dtt/dtt.tv', Directory + '/Settings/Temp/TerrestrialChannelListArchive')
				return True
			except:
				pass

		NameDirectory = ResearchBouquetTerrestrial('terr', 'dtt')
		if not NameDirectory:
			NameDirectory = ForceSearchBouquetTerrestrial()
		try:
			shutil.copyfile(NameDirectory, Directory + '/Settings/Temp/TerrestrialChannelListArchive')
			return True
		except:
			pass

	Service = SaveTrasponderService(lamedb)
	if Service:
		if not SaveBouquetTerrestrial(type):
			CreateBouquetForce()
		return True


def TransferBouquetTerrestrialFinal():

	def WritingTerrestrial():
		try:
			OpenBouquet = open('/etc/enigma2/userbouquet.SettingsDtt.tv', 'w')
			OpenBouquet.write('#NAME CST\xae DTT\n')
			OpenBouquet.close()
			RewriteBouquet = open('/etc/enigma2/bouquets.tv').readlines()
			WriteBouquet = open('/etc/enigma2/bouquets.tv', 'w')
			Counter = 0
			for xx in RewriteBouquet:
				if not xx.find('SettingsDtt') != -1:
					if Counter == 2:
						WriteBouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.SettingsDtt.tv" ORDER BY bouquet\n')
						WriteBouquet.write(xx)
					else:
						WriteBouquet.write(xx)
					Counter = Counter + 1

			WriteBouquet.close()
			return '/etc/enigma2/userbouquet.SettingsDtt.tv'
		except:
			return

	def RestoreTerrestrial():
		for file in os.listdir('/etc/enigma2/'):
			if re.search('^userbouquet.*.tv', file):
				f = open('/etc/enigma2/' + file, 'r')
				x = f.read()
				if re.search('#NAME CST\xae DTT', x, flags=re.IGNORECASE):
					return '/etc/enigma2/' + file

		return WritingTerrestrial()

	try:
		TerrestrialChannelListArchive = open(Directory + '/Settings/Temp/TerrestrialChannelListArchive').readlines()
		DirectoryUserBouquetTerrestrial = RestoreTerrestrial()
		if DirectoryUserBouquetTerrestrial:
			TrasfBouq = open(DirectoryUserBouquetTerrestrial, 'w')
			for Line in TerrestrialChannelListArchive:
				if Line.lower().find('#name') != -1:
					TrasfBouq.write('#NAME CST\xae DTT\n')
				else:
					TrasfBouq.write(Line)

			TrasfBouq.close()
			return True
	except:
		return False


def StartProcess(jLinkSat, jLinkDtt, Type, Personal):

	def LamedbRestore():
		try:
			TrasponderListNewLamedb = open(Directory + '/Settings/Temp/TrasponderListNewLamedb', 'w')
			ServiceListNewLamedb = open(Directory + '/Settings/Temp/ServiceListNewLamedb', 'w')
			inTransponder = False
			inService = False
			infile = open('/etc/enigma2/lamedb')
			while 1:
				line = infile.readline()
				if not line:
					break
				if not (inTransponder or inService):
					if line.find('transponders') == 0:
						inTransponder = True
					if line.find('services') == 0:
						inService = True
				if line.find('end') == 0:
					inTransponder = False
					inService = False
				if inTransponder:
					TrasponderListNewLamedb.write(line)
				if inService:
					ServiceListNewLamedb.write(line)

			TrasponderListNewLamedb.close()
			ServiceListNewLamedb.close()
			WritingLamedbFinal = open('/etc/enigma2/lamedb', 'w')
			WritingLamedbFinal.write('eDVB services /4/\n')
			TrasponderListNewLamedb = open(Directory + '/Settings/Temp/TrasponderListNewLamedb').readlines()
			for x in TrasponderListNewLamedb:
				WritingLamedbFinal.write(x)

			try:
				TrasponderListOldLamedb = open(Directory + '/Settings/Temp/TrasponderListOldLamedb').readlines()
				for x in TrasponderListOldLamedb:
					WritingLamedbFinal.write(x)

			except:
				pass

			WritingLamedbFinal.write('end\n')
			ServiceListNewLamedb = open(Directory + '/Settings/Temp/ServiceListNewLamedb').readlines()
			for x in ServiceListNewLamedb:
				WritingLamedbFinal.write(x)

			try:
				ServiceListOldLamedb = open(Directory + '/Settings/Temp/ServiceListOldLamedb').readlines()
				for x in ServiceListOldLamedb:
					WritingLamedbFinal.write(x)

			except:
				pass

			WritingLamedbFinal.write('end\n')
			WritingLamedbFinal.close()
			return True
		except:
			return False

	def DownloadSettingAggDtt(jLinkDtt):
		try:
			req = urllib2.Request(jLinkDtt)
			req.add_header('User-Agent', 'SatvenusSettings')
			response = urllib2.urlopen(req)
			link = response.read()
			response.close()
			Setting = open(Directory + '/Settings/Temp/listaE2dtt.zip', 'w')
			Setting.write(link)
			Setting.close()
			if os.path.exists(Directory + '/Settings/Temp/listaE2dtt.zip'):
				os.system('mkdir ' + Directory + '/Settings/Temp/settingdtt')
				try:
					os.system('unzip ' + Directory + '/Settings/Temp/listaE2dtt.zip -d  ' + Directory + '/Settings/Temp/settingdtt')
				except:
					pass

				os.system('mkdir ' + Directory + '/Settings/Temp/enigma2dtt')
				os.system('find ' + Directory + '/Settings/Temp/settingdtt -type f -print | sed \'s/ /" "/g\'| awk \'{ str=$0; sub(/\\.\\//, "", str); gsub(/.*\\//, "", str);print "mv " $0 " ' + Directory + '/Settings/Temp/enigma2dtt/"str }\' | sh')
				if os.path.exists(Directory + '/Settings/Temp/enigma2dtt/lamedb'):
					return True
			return False
		except:
			return

	def DownloadSettingAgg(jLinkSat, jLinkDtt):
		conferma = True
		if jLinkDtt and str(jLinkDtt) != '0':
			if DownloadSettingAggDtt(jLinkDtt):
				conferma = True
			else:
				onferma = False
		try:
			req = urllib2.Request(jLinkSat)
			req.add_header('User-Agent', 'SatvenusSettings')
			response = urllib2.urlopen(req)
			link = response.read()
			response.close()
			Setting = open(Directory + '/Settings/Temp/listaE2.zip', 'w')
			Setting.write(link)
			Setting.close()
			if os.path.exists(Directory + '/Settings/Temp/listaE2.zip'):
				os.system('mkdir ' + Directory + '/Settings/Temp/setting')
				try:
					os.system('unzip ' + Directory + '/Settings/Temp/listaE2.zip -d  ' + Directory + '/Settings/Temp/setting')
				except:
					pass

				os.system('mkdir ' + Directory + '/Settings/Temp/enigma2')
				os.system('find ' + Directory + '/Settings/Temp/setting -type f -print | sed \'s/ /" "/g\'| awk \'{ str=$0; sub(/\\.\\//, "", str); gsub(/.*\\//, "", str);print "mv " $0 " ' + Directory + '/Settings/Temp/enigma2/"str }\' | sh')
				if os.path.exists(Directory + '/Settings/Temp/enigma2/lamedb') and conferma:
					return True
			return False
		except:
			return

	def SaveList(list):
		jw = open('/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Moduli/Settings/SelectBack', 'w')
		for dir, name in list:
			jw.write(dir + '---' + name + '\n')

		jw.close()

	def SavePersonalSetting():
		try:
			os.system('mkdir ' + Directory + '/Settings/SelectFolder')
			jw = open('/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Moduli/Settings/Select')
			jjw = jw.readlines()
			jw.close()
			count = 1
			list = []
			for x in jjw:
				try:
					jx = x.split('---')
					newfile = 'userbouquet.GioppyGio' + str(count) + '.tv'
					os.system('cp /etc/enigma2/' + jx[0] + ' /' + Directory + '/Settings/SelectFolder/' + newfile)
					list.append((newfile, jx[1]))
					count = count + 1
				except:
					pass

			SaveList(list)
		except:
			return

		return True

	def TransferPersonalSetting():
		try:
			jw = open('/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Moduli/Settings/SelectBack')
			jjw = jw.readlines()
			jw.close()
			for x in jjw:
				try:
					jx = x.split('---')
					os.system('cp -rf ' + Directory + '/Settings/SelectFolder/*' + jx[0] + '  /etc/enigma2/')
				except:
					pass

		except:
			pass

		return True

	def CreateUserbouquetPersonalSetting():
		try:
			jw = open('/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Moduli/Settings/SelectBack')
			jjw = jw.readlines()
			jw.close()
		except:
			pass

		jRewriteBouquet = open('/etc/enigma2/bouquets.tv')
		RewriteBouquet = jRewriteBouquet.readlines()
		jRewriteBouquet.close()
		WriteBouquet = open('/etc/enigma2/bouquets.tv', 'w')
		Counter = 0
		for xx in RewriteBouquet:
			if Counter == 1:
				for x in jjw:
					if x[0].strip() != '':
						try:
							jx = x.split('---')
							WriteBouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + jx[0].strip() + '" ORDER BY bouquet\n')
						except:
							pass

				WriteBouquet.write(xx)
			else:
				WriteBouquet.write(xx)
			Counter = Counter + 1

		WriteBouquet.close()

	def TransferNewSetting():
		try:
			os.system('rm -rf /etc/enigma2/lamedb')
			os.system('rm -rf /etc/enigma2/*.radio')
			os.system('rm -rf /etc/enigma2/*.tv')
			eDVBDB.getInstance().removeServices()
			os.system('cp -rf ' + Directory + '/Settings/Temp/enigma2/*.tv  /etc/enigma2/')
			os.system('cp -rf ' + Directory + '/Settings/Temp/enigma2/*.radio  /etc/enigma2/')
			os.system('cp -rf ' + Directory + '/Settings/Temp/enigma2/lamedb  /etc/enigma2/')
			if not os.path.exists('/etc/enigma2/blacklist'):
				os.system('cp -rf ' + Directory + '/Settings/Temp/enigma2/blacklist /etc/enigma2/')
			if not os.path.exists('/etc/enigma2/whitelist'):
				os.system('cp -rf ' + Directory + '/Settings/Temp/enigma2/whitelist /etc/enigma2/')
			os.system('cp -rf ' + Directory + '/Settings/Temp/enigma2/satellites.xml /etc/tuxbox/')
		except:
			return

		return True

	Status = True
	if int(Type) == 1:
		SavingProcessTerrestrialChannels = StartSavingTerrestrialChannels('/etc/enigma2/lamedb', False)
		os.system('cp -r /etc/enigma2/ ' + Directory + '/Settings/enigma2')
	if not DownloadSettingAgg(jLinkSat, jLinkDtt):
		os.system('cp   ' + Directory + '/Settings/enigma2/* /etc/enigma2')
		os.system('rm -fr ' + Directory + '/Settings/enigma2')
		Status = False
	else:
		if int(Type) == 0:
			SavingProcessTerrestrialChannels = StartSavingTerrestrialChannels(Directory + '/Settings/Temp/enigma2dtt/lamedb', True)
		personalsetting = False
		if int(Personal) == 1:
			personalsetting = SavePersonalSetting()
		if TransferNewSetting():
			if personalsetting:
				if TransferPersonalSetting():
					CreateUserbouquetPersonalSetting()
					os.system('rm -fr ' + Directory + '/Settings/SelectFolder')
					os.system('mv /usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Moduli/Settings/SelectBack /usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Moduli/Settings/Select')
			os.system('rm -fr ' + Directory + '/Settings/enigma2')
		else:
			os.system('cp   ' + Directory + '/Settings/enigma2/* /etc/enigma2')
			os.system('rm -fr ' + Directory + '/Settings/Temp/*')
			Status = False
		if SavingProcessTerrestrialChannels and Status:
			if LamedbRestore():
				TransferBouquetTerrestrialFinal()
	os.system('rm -fr ' + Directory + '/Settings/Temp/*')
	return Status


class ScreenMessage(Screen):
	global MyMessage
	def __init__(self, session = None):
		Screen.__init__(self, session)
		skin = '/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/Skin/Message.xml'
		f = open(skin, 'r')
		self.skin = f.read()
		f.close()
		self['text'] = Label(MyMessage)

	def gotSession(self, session):
		self.session = session
		self.Messageinfo = session.instantiateDialog(ScreenMessage)


class GioppyGioSettings:

	def __init__(self, session = None):
		self.session = session
                self.iTimer1 = eTimer()
                self.iTimer2 = eTimer()
                self.iTimer3 = eTimer()
		self.iTimer4 = eTimer()
		self.iTimer1.callback.append(self.startTimerSetting)
		self.iTimer2.callback.append(self.startTimerSetting)
		self.iTimer3.callback.append(self.startTimerSetting)
		self.iTimer4.callback.append(self.StopMessage)

	def gotSession(self, session):
		self.session = session
		Type, AutoTimer, Personal, NumberSat, NameSat, Date, NumberDtt, DowDate, NameInfo = Load()
		if int(AutoTimer) == 1:
			self.TimerSetting()

	def StopTimer(self):
		try:
			self.iTimer1.stop()
		except:
			pass

		try:
			self.iTimer2.stop()
		except:
			pass

		try:
			self.iTimer3.stop()
		except:
			pass

	def TimerSetting(self):
		try:
			self.StopTimer()
		except:
			pass

		now = time.time()
		ttime = time.localtime(now)
                start_time1 = time.mktime([ttime[0], ttime[1], ttime[2], 6, MinStart, 0, ttime[6], ttime[7], ttime[8]])
                start_time2 = time.mktime([ttime[0], ttime[1], ttime[2], 14, MinStart, 0, ttime[6], ttime[7], ttime[8]])
                start_time3 = time.mktime([ttime[0], ttime[1], ttime[2], 22, MinStart, 0, ttime[6], ttime[7], ttime[8]])
		if start_time1 < now + 60:
			start_time1 += 86400
		if start_time2 < now + 60:
			start_time2 += 86400
		if start_time3 < now + 60:
			start_time3 += 86400
		delta1 = int(start_time1 - now)
		delta2 = int(start_time2 - now)
		delta3 = int(start_time3 - now)
		self.iTimer1.start(1000 * delta1, True)
		self.iTimer2.start(1000 * delta2, True)
		self.iTimer3.start(1000 * delta3, True)

	def StopMessage(self):
		try:
			self.iTimer4.stop()
		except:
			pass

		self.iScreenMessage.Messageinfo.hide()

	def StartMessage(self):
		self.iScreenMessage = ScreenMessage()
		self.iScreenMessage.gotSession(self.session)
		self.iScreenMessage.Messageinfo.show()

	def startTimerSetting(self, Auto = False):
		global MyMessage
		Type, AutoTimer, Personal, NumberSat, NameSat, Date, NumberDtt, DowDate, NameInfo = Load()

		def OnDsl():
			try:
				urllib2.urlopen('http://www.google.com', None, 3)
				return True
			except:
				return False

			return

		if OnDsl():
				for jNumberSat, jNameSat, jLinkSat, jDateSat, jNumberDtt, jNameDtt, jLinkDtt, jDateDtt in DownloadSetting():
					jDate = jDateSat
					if jDateDtt:
						if int(jDateDtt) > int(jDateSat):
							jDate = jDateDtt
					if jNumberSat == NumberSat and NumberDtt == jNumberDtt:
						if jDate > Date or AutoTimer:
							if StartProcess(jLinkSat, jLinkDtt, Type, Personal):
								now = time.time()
								jt = time.localtime(now)
								DowDate = str(jt[2]).zfill(2) + '-' + str(jt[1]).zfill(2) + '-' + str(jt[0]) + '   ' + str(jt[3]).zfill(2) + ':' + str(jt[4]).zfill(2) + ':' + str(jt[5]).zfill(2)
								WriteSave(Type, AutoTimer, Personal, jNumberSat, jNameSat, jDateSat, jNumberDtt, DowDate, NameInfo)
								OnclearMem()
								eDVBDB.getInstance().reloadServicelist()
								eDVBDB.getInstance().reloadBouquets()
							        MyMessage = _(' ') + ' ' + NameInfo + _('\n:from\n') + ConverDate(jDate) + _('\ninstalled !')
							else:
								MyMessage = _('Sorry, cannot download !')
						else:
							MyMessage = _('New:\n') + ConverDate(jDate) + _('Old:\n') + ConverDate(Date)
						break

		else:
			MyMessage = _('Sorry.\nno internet connection !')
		self.StartMessage()
		self.iTimer4.start(1800, True)
		self.TimerSetting()

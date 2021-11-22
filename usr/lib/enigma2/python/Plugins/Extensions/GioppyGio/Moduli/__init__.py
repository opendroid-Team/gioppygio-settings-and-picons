#from Source.LocaleInit import _
# GioppyGio: [Translation] begin
# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE
import os
import gettext
import sys

PluginLanguageDomain = "GioppyGio"
PluginLanguagePath = "/usr/lib/enigma2/python/Plugins/Extensions/GioppyGio/locale/"

def localeInit():
    lang = language.getLanguage()[:2]
    os.environ['LANGUAGE'] = lang
    gettext.bindtextdomain(PluginLanguageDomain, PluginLanguagePath)
    gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE, ''))

def _(txt):
    t = gettext.dgettext(PluginLanguageDomain, txt)
    if t == txt:
        t = gettext.dgettext('enigma2', txt)
    return t

localeInit()
language.addCallback(localeInit)
# GioppyGio: [Translation] end

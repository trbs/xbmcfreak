import os, logging

rootDir = os.getcwd().replace(";","")
rootDir = os.path.join(rootDir, '')

cacheDir = os.path.join(rootDir,'cache','')

cacheValidTime = 7*24*3600
webTimeOut = 30

appName = "XOT-Uzg (XOT-Uzg.v3)"
appSkin = "uzg-progwindow.xml"
contextMenuSkin = "uzg-contextmenu.xml"
updaterSkin = "xot-updater.xml"

logLevel = logging.DEBUG
logDual = True
logFileName = "uzg.log"
logFileNamePlugin = "uzgPlugin.log"

xotDbFile = os.path.join(rootDir,"xot.db")

version = "3.2.0b6"
updateUrl = "http://www.rieter.net/uitzendinggemist/index.php?currentversion="

skinFolder = "" #get's set from default.py
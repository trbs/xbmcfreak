#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================

import os, re, string, sys, time
from string import *
import htmlentitydefs
import beautifulsoup

import xbmc

#===============================================================================
# Make global object available
#===============================================================================
import config, envcontroller
logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler
#===============================================================================
    
#===============================================================================
def DoRegexFindAll(regex, data):
    try:
        result = re.compile(regex, re.DOTALL + re.IGNORECASE)
        return result.findall(data)
    except:
        logFile.critical('error regexing', exc_info=True)
        return []

#============================================================================== 
def DoSoupFindAll(data, name=None, attrs={}, recursive=True, text=None, limit=None, **kwargs):
    try:
        soup = beautifulsoup.BeautifulSoup(data)
        return soup.findAll(name, attrs, recursive, text, limit, **kwargs)
    except:
        logFile.debug("Error parsing using soup", exc_info=True)
        return []

#===============================================================================
def GetSkinFolder():
    skinName = xbmc.getSkinDir()
    if (os.path.exists(os.path.join(config.rootDir,"resources","skins",skinName))):
        skinFolder = skinName
    else:
        skinFolder = "Default"
    logFile.info("Setting Skin to: " + skinFolder)
    return skinFolder

#===============================================================================
def DirectoryPrinter(dir):
    try:
        version = xbmc.getInfoLabel("system.buildversion")
        buildDate = xbmc.getInfoLabel("system.builddate")
        env = envcontroller.EnvController().GetEnvironment(True)
        logFile.debug("XBMC Information: \nVersion: XBMC %s\nEnvironment: %s\nBuildDate: %s)", version, env, buildDate)
        
        dirWalker = os.walk(dir)
        dirPrint = "Folder Structure of %s" % (config.appName)
        
        excludePattern = os.path.join('a','.svn').replace("a","")
        for dir, folders, files in dirWalker:
            if dir.count(excludePattern) == 0:
                for file in files:
                    if not file.startswith(".") and not file.endswith(".pyo"):
                        dirPrint = "%s\n%s" % (dirPrint, os.path.join(dir, file))
        logFile.debug("%s" % (dirPrint))
    except:
        logFile.critical("Error printing folder %s", dir, exc_info=True)        
        
#===============================================================================
def CacheCleanUp():
    try:
        deleteCount = 0
        fileCount = 0
        for item in os.listdir(config.cacheDir):
            fileName = os.path.join(config.cacheDir, item)
            if os.path.isfile(fileName):
                fileCount = fileCount + 1
                createTime = os.path.getctime(fileName)
                if createTime + config.cacheValidTime < time.time():
                    os.remove(fileName)
                    deleteCount = deleteCount + 1
        logFile.info("Removed %s of %s files from cache.", deleteCount, fileCount)
    except:
        logFile.critical("Error cleaning the cachefolder", exc_info=True)    
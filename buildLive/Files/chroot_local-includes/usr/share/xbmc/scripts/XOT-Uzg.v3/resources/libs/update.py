#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================

import sys
import xbmcgui

#===============================================================================
# Make global object available
#===============================================================================
import config
logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler

#===============================================================================
def CheckVersion(version, updateUrl, verbose = False):
    if updateUrl == "" or updateUrl == None:
        return
    
    recentVersion = GetLatestVersion(version, updateUrl)
    if recentVersion!=0:
        logFile.info("New version available: %s", recentVersion)
        dialog = xbmcgui.Dialog()
        dialog.ok("New Version Available.","A new version of %s is \navailable. Please visit the website to \ndownload version %s" % (config.appName, recentVersion))
    elif verbose:
        dialog = xbmcgui.Dialog()
        dialog.ok("No Updates","There is no new version of the XOT Framework")        
    return

#===============================================================================
def GetLatestVersion(currentVersion, updateUrl):
    _newVersion = False
    _url = updateUrl+currentVersion
    data = uriHandler.Open(_url, pb=False)
    if data == "" or data=="0":
        return 0
    else:
        return data


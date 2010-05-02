#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================

import exceptions
import xml.dom.minidom
import sys, os, re
import helpers
from helpers import database

#===============================================================================
# Make global object available
#===============================================================================
import config
import common
logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler

def CleanupXml(xmlDoc):
    #cleanup
    prettyXml = xmlDoc.toprettyxml()
    #remove not needed lines with only whitespaces
    prettyXml = re.sub("(?m)^\s+[\n\r]", "", prettyXml, )
    
    prettyXml = re.sub("[\n\r]+\t+([^<\t]+)[\n\r]+\t+", "\g<1>", prettyXml)
    return prettyXml

def LoadFavorites(channel):
    """
        Reads the favorites into items.
    """
    try:
        db = database.DatabaseHandler()
        items = db.LoadFavorites(channel)
        for item in items:
            item.icon = channel.icon
    except:
        logFile.error("Settings :: Error loading favorites", exc_info=True)
           
    return items


def AddToFavorites(item, channel):
    """
        Adds an items to the favorites
    """
    try:
        db = database.DatabaseHandler()
        db.AddFavorite(item.name, item.url, channel)
    except:
        logFile.error("Settings :: Error adding favorites", exc_info=True)
              

def RemoveFromFavorites(item, channel):
    try:
        db = database.DatabaseHandler()
        db.DeleteFavorites(item.name, item.url, channel)
    except:
        logFile.error("Settings :: Error removing from favorites", exc_info=True)
    return

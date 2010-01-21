#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================
import sys, re, string
from string import *

import htmlentitydefs
logFile = sys.modules['__main__'].globalLogFile

class HtmlEntityHelper:
    #================================================================================
    # Used for HTML converting
    #================================================================================
    def __init__(self):
        return
    
    #===============================================================================
    def StripAmp (data):
        return replace(data, "&amp;","&")

    #================================================================================
    # Static method wrappers
    #================================================================================    
    def ConvertURLEntities(url):
        htmlHelper = HtmlEntityHelper()
        return htmlHelper.__ConvertURLEntities(url)
    
    def ConvertHTMLEntities(html):
        htmlHelper = HtmlEntityHelper()
        return htmlHelper.__ConvertHTMLEntities(html)
    
    #============================================================================== 
    def __ConvertHTMLEntities(self, html):
        """
            Convert the entities in HTML using the HTMLEntityConverter
        """
        newHtml = re.sub("&(#?)(.+?);", self.__HTMLEntityConverter, html)
        return newHtml
    
    #============================================================================== 
    def __ConvertURLEntities(self, url):
        """
            Convert the entities in an URL using the UrlEntityConverter
        """
        newUrl = re.sub("(%)([1234567890ABCDEF]{2})", self.__UrlEntityConverter, url)
        return newUrl
        
    #===============================================================================
    def __HTMLEntityConverter(self, entity):
        #logFile.debug("1:%s, 2:%s", entity.group(1), entity.group(2))
        try:
            if entity.group(1)=='#':
                #logFile.debug("%s: %s", entity.group(2), chr(int(entity.group(2))))
                return chr(int(entity.group(2)))
            else:
                #logFile.debug("%s: %s", entity.group(2), htmlentitydefs.entitydefs[entity.group(2)])
                return htmlentitydefs.entitydefs[entity.group(2).lower()]
        except:
            logFile.error("error converting HTMLEntities", exc_info=True)
            return '&%s%s;' % (entity.group(1),entity.group(2))
        return entity
    
    #============================================================================== 
    def __UrlEntityConverter(self, entity):
        """
           Substitutes an HTML/URL entity with the correct character
        """
        #logFile.debug("1:%s, 2:%s", entity.group(1), entity.group(2))
        try:
            tmpHex = '0x%s' % (entity.group(2))
            #logFile.debug(int(tmpHex, 16))
            return chr(int(tmpHex, 16))
        except:
            logFile.error("error converting URLEntities", exc_info=True)
            return '%s%s' % (entity.group(1),entity.group(2))
    
    #===============================================================================
    # Static method descriptions        
    #===============================================================================
    ConvertHTMLEntities = staticmethod(ConvertHTMLEntities)
    ConvertURLEntities = staticmethod(ConvertURLEntities)
    StripAmp = staticmethod(StripAmp)
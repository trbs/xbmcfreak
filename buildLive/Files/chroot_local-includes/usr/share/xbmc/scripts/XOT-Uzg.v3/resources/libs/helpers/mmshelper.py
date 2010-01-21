#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================

import os, re, string, sys, time, types
import common

#===============================================================================
# Make global object available
#===============================================================================

logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler
#===============================================================================
class MmsHelper:
    def __init__(self):
        raise NotImplementedError
        
    #===========================================================================
    # Decodes a HTTP MMS playlist into a MMS stream
    #===========================================================================
    @staticmethod
    def GetMmsFromHtml(url):
        if url.find(".mms") > 0:
            logFile.info("MMS found in url: %s", url)
            return url
                
        logFile.debug("Parsing %s to find MMS", url)
        data = uriHandler.Open(url, pb=True)
        urls = common.DoRegexFindAll("[Rr]ef\d=http://([^\r\n]+)", data)
        #logFile.debug(urls)
                
        if len(urls) > 0:
            return "mms://%s" % (urls[0],)
        else:
            return url
#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================
import re, sys
import common
from helpers import htmlentityhelper

logFile = sys.modules['__main__'].globalLogFile

class Algorithms:
    """
        Contains all algorithms for decoding urls to media-urls
    """
    
    #=========================================================================== 
    def ExtractMediaUrl(self, url, data):
        """
            returns the full media url for the given url and code
        """
        
        #========================================================= Megavideo.com
        if url.find("megavideo.com") > 0:
            #the usual decode which is:
            # a replacement of the 
            #"flv","UIIM%07%12%12JJJ%0D%08%13PXZ%5CKTYXR%13%5ERP%12%5BTQXN%12X%0DX%5E%09%0CY%0B%5E%05%0B%04X%08%04%0F%0A%0C%0E%08%5E%5E%0C%04%08Y%5B%04%0B%0C%0D%0D%12
            #       http:  /  /  www0  5  .  mega  video.  c  om/  f  iles/  e0  ec  4  1  d6  c  8  6  9  e5  9  2  7  1  3  5  c  c  1  9  5  df  9  6  1  0  0  / 
            #http://www05.megavideo.com/files/e0ec41d6c869e5927135cc195df96100/
            
            codeRegex = 'addVariable\("flv","([^"]+)"\)'
            codeResults = re.findall(codeRegex, data, re.DOTALL + re.IGNORECASE)
            
            if len(codeResults) > 0:
                code = codeResults[-1]
                dictionary = {"_": "b", "I": "t", "J": "w", "K": "v", "M": "p", "N": "s", "P": "m", "Q": "l", "R": "o", "T": "i", "U": "h", "X": "e", "Y": "d", "Z": "g", "%04": "9", "%05": "8", "%07": ":", "%08": "5", "%09": "4", "%0A": "7", "%0B": "6", "%0C": "1", "%0D": "0", "%0E": "3", "%0F": "2", "%12": "/", "%13": ".", "%5B": "f", "%5C": "a", "%5E": "c"}
                return self.RegexReplaceDictionary(code, dictionary) 
            else:
                return ""
        
        #=========================================================== youtube.com
        elif url.find("youtube.com") > 0:
            # idea from http://linux.byexamples.com/archives/302/how-to-wget-flv-from-youtube/
            
            mediaRegex = "var fullscreenUrl = '/[^']+(video_id=[^']+)title="
            mediaResults = re.findall(mediaRegex, data, re.DOTALL + re.IGNORECASE)
            
            if len(mediaResults) > 0:
                lastPart = mediaResults[-1]
                mediaUrl = "%s%s" % ("http://www.youtube.com/get_video.php?", lastPart)
                return mediaUrl 
            else:
                return ""
            
        #============================================================== veoh.com
        elif url.find("veoh.com") > 0:
            #===================================================================
            # This will only retrieve the first 25 MB
            #===================================================================
            # taken from http://www.jeroenwijering.com/?thread=5665#msg27949
            #fullPreviewHashPath="http://content.veoh.com/flash/p/6279991/0901638753f53dc6515f7624ae6dd13753308925.flv?ct=9137981c7c86355d639a9291d56c28ada1d5a82d8faabe50"
            mediaRegex = 'fullPreviewHashPath="([^"]+)"'
            mediaResults = re.findall(mediaRegex, data, re.DOTALL+re.IGNORECASE)
            
            if len(mediaResults) > 0:
                return mediaResults[-1]
            else:
                return ""
            
            # NOT WORKING ANYMORE method 2 taken from http://board.alluc.org/viewtopic.php?pid=433097
            #http://www.veoh.com/videos/v1990401qg3bdNEa  <-- This is the link to the video, the PermalinkID is the last part starting with "v199..."
            #http://www.veoh.com/rest/video/v1990401qg3bdNEa/details  <-- This gets you the information page.
            #originalHash="94f05afdb2d7d1bcb8289bdfb325c51f73874B1O"  <-- This is just an example of what you might see.
            #origExtension=".avi"  <-- This is the type of the original file that was uploaded.
            #Use the template above and you get: http://p-cache.veoh.com/cache/external/94f05afdb2d7d1bcb8289bdfb325c51f73874B1O.avi?v1990401qg3bdNEa
            # originalHash="a5c40e07ae0730d1edc6ea99ded7195a79fc2e2b" origExtension=".mp4"
            
            #hashRegex = 'originalHash="([^"]+)"'
            #extRegex = 'origExtension="([^"]+)"'
            #idRegex = 'permalinkId="([^"]+)"'
            #
            #hashResults = re.findall(hashRegex, data, re.DOTALL+re.IGNORECASE) 
            #extResults = re.findall(extRegex, data, re.DOTALL+re.IGNORECASE)
            #idResults =  re.findall(idRegex, data, re.DOTALL+re.IGNORECASE)
            #
            #if len(hashResults) > 0 and len(extResults) > 0 and len(idResults) > 0:
            #    #url = "http://p-cache.veoh.com/cache/external/%s%s?permalinkld=%s" % (hashResults[-1], extResults[-1], idResults[-1])                
            #    url = "http://ex-cache.veoh.com/cache/external/%s%s?permalinkld=%s" % (hashResults[-1], extResults[-1], idResults[-1])                
            #    return url 
            #else:
            #    return ""
        
        #==============================================================================
        elif url.find("video.google.com") > 0:
            # extract the url
            mediaRegex = "googleplayer.swf\?&videoUrl=([^ ]+)"
            mediaResults = re.findall(mediaRegex, data, re.DOTALL+re.IGNORECASE)
            
            if len(mediaResults) > 0:
                mediaUrl = mediaResults[-1]
                
                # replace the entities and return the value    
                return htmlentityhelper.HtmlEntityHelper.ConvertURLEntities(mediaUrl)
            else:
                return ""            
                    
        return "Nothing"
    
    
    #=========================================================================== 
    def DecodeItemUrl(self, url):
        """
            Converts a coded URL to a real one 
        """
        
        #========================================================= Megavideo.com
        if url.find("megavideo.com") > 0:
            #http://www.megavideo.com/v/QS7N924R0b5aac3284b34463fa9e6aeea929bb58.8531586.0
            #http://www.megavideo.com/?v=QS7N924R
            if url.find("/?") < 1:
                # do the url rewrite version
                regex = re.compile(r'(http://[^/]+/)v/(.{8}).*', re.VERBOSE)
                url = regex.sub(r'\1?v=\2',url)
            
            return url
        #=========================================================== youtube.com
        elif url.find("youtube.com") > 0:
            return url
            
        #============================================================== veoh.com
        elif url.find("veoh.com") > 0:
            # taken from http://www.jeroenwijering.com/?thread=5665#msg27949
            # http://www.veoh.com/videos/v669398tRxFQc4d?cmpTag=featured&rank=0                                         
            # http://www.veoh.com/rest/video/v669398tRxFQc4d/details
            if url.find("/rest/video") > 0:
                return url
            
            regex = re.compile(r'http://www.veoh.com/videos/([^?%/]+)([\w\W]+)')
            url = regex.sub(r'http://www.veoh.com/rest/video/\1/details', url)
            return url
        
        #============================================================================== 
        elif url.find("googleplayer.swf") > 0:
            #http://video.google.com/googleplayer.swf\?docId=([^"]+)
            regex = re.compile('http://video.google.com/googleplayer.swf\?docId=(.+)',  re.DOTALL + re.IGNORECASE)
            results = regex.findall(url)
            
            if len(results) > 0:
                return "http://video.google.com/videoplay?docid=%s" % results[-1]
            else:
                return ""            
        
        #========================================================= We don't know
        else:
            return "Nothing"
                
    #============================================================================
    # Helper fuctions     
    #============================================================================
    def RegexReplaceDictionary(self, string, dictionary):
        """
            take a text and replace words that match a key in a dictionary with
            the associated value, return the changed text
        """
        rc = re.compile('|'.join(map(re.escape, dictionary)))
        
        def Translate(match):
            return dictionary[match.group(0)]
        
        return rc.sub(Translate, string)

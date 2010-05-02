from uriopener import UriHandler
from cgi import logfile
import uriopener
import xbmc, xbmcgui
import sys, re, urllib, math, urlparse, types, string
#===============================================================================
# Make global object available
#===============================================================================
import common
import mediaitem
import config
import controls
import contextmenu
import chn_class
from helpers import htmlentityhelper

logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler
#===============================================================================
# register the channels
#===============================================================================
if (sys.modules.has_key('progwindow')):
    register = sys.modules['progwindow']
elif (sys.modules.has_key('plugin')):
    register = sys.modules['plugin']
#register.channelButtonRegister.append(105)
register.channelRegister.append('chn_svt.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder)')

#===============================================================================
# main Channel Class
#===============================================================================
class Channel(chn_class.Channel):
    #===============================================================================
    # define class variables
    #===============================================================================
    def InitialiseVariables(self):
        """
        Used for the initialisation of user defined parameters. All should be 
        present, but can be adjusted
        """
        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self)
        
        self.guid = "06DB83A2-42F4-11DD-AAC1-CEFD55D89593"
        self.mainListUri = "http://svtplay.se/alfabetisk"
        self.baseUrl = "http://svtplay.se/"
        self.icon = "svticon.png"
        self.iconLarge = "svtlarge.png"
        self.noImage = "svtimage.png"
        self.channelName = "Sveriges Television"
        self.channelDescription = u'Sända från SVT'
        self.moduleName = "chn_svt.py"
        self.maxXotVersion = "3.2.0"
        
        #self.backgroundImage = ""
        #self.backgroundImage16x9 = ""
        self.requiresLogon = False
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
        
        
        self.episodeItemRegex = '<li>\W+<a href="([^"]+)">([^<]+)</a>\W+</li>'
        self.videoItemRegex = '<li class="[^"]*"\W*>\W+<a href="([^"]+)"[^>]+title="([^"]*)"[^>]+>\W+<img[^>]+src="([^"]+)[^>]+>\W+(<!--[^/]+/span -->\W+){0,1}<span[^>]*>([^<]+)</span>'
        self.folderItemRegex = '<li class="">\W+<a href="([^"]+)"[^>]+>([^<]+)</a>\W+'
        #self.mediaUrlRegex = '<param name="flashvars" value="pathflv\W*=\W*([^&]+)(_definst_){0,1}/([^&]+)&amp;'
        
        """ 
            The ProcessPageNavigation method will parse the current data using the pageNavigationRegex. It will
            create a pageItem using the CreatePageItem method. If no CreatePageItem method is in the channel,
            a default one will be created with the number present in the resultset location specified in the 
            pageNavigationRegexIndex and the url from the combined resultset. If that url does not contain http://
            the self.baseUrl will be added. 
        """
        # remove the &amp; from the url
        self.pageNavigationRegex = 'link button-->\W+<li class="[^"]*"><a href="([^"]+)"[^>]+>(\d+)'  
        self.pageNavigationRegexIndex = 1

        #========================================================================== 
        # non standard items
        self.categoryName = ""
        self.currentUrlPart = ""
        
        return True
    
    #============================================================================== 
    def PreProcessFolderList(self, data):
        """
        Accepts an data from the ProcessFolderList Methode, BEFORE the items are
        processed. Allows setting of parameters (like title etc). No return value!
        """
        logFile.info("Performing Pre-Processing")
        _items = []
        
        regex = '<li class=".*irst-child selected[^">]*">\W+<a href="/([^="?]+)(/[^"]+)*"'
        result = common.DoRegexFindAll(regex, data)
        
        if len(result) > 0:
            self.currentUrlPart = "%s%s/" % (self.baseUrl, result[0][0])
            logFile.debug(self.currentUrlPart)
        
        #chop not needed part:
        end = string.find(data, 'showBrowserModule.extra')
        data = common.DoRegexFindAll('[\w\W]{%s}' % (end,), data)[0]
        return (data, _items)
    
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        item = mediaitem.MediaItem(resultSet[1], htmlentityhelper.HtmlEntityHelper.StripAmp(urlparse.urljoin(self.baseUrl, resultSet[0])))
        item.description = "%s%s" % (self.categoryName, item.name)
        item.icon = self.icon
        return item
    
    #==============================================================================
    def CreatePageItem(self, resultSet):
        """
        Accepts an resultset
        """
        logFile.debug("Starting CreatePageItem")
        total = self.currentUrlPart
        
        for set in resultSet:
            total = "%s%s" % (total,set)
        
        total = htmlentityhelper.HtmlEntityHelper.StripAmp(total)
        
        if not self.pageNavigationRegexIndex == '':
            item = mediaitem.MediaItem(resultSet[self.pageNavigationRegexIndex], urlparse.urljoin(self.baseUrl, total))
        else:
            item = mediaitem.MediaItem("0")            
        
        item.type = "page"
        logFile.debug("Created '%s' for url %s", item.name, item.url)
        return item 
    
    #==============================================================================
    def CreateFolderItem(self, resultSet):
        # <div class="enddep"><a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>\W*</div>
        #                                      0            1
        # <td class="image"><a[^>]+><img[^>]+src="([^"]+)"[^>]+></a></td>\W+<td[^>]+><div[^>]+><div class="enddep"><a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>\W*</div>
        #                         
        #                   0                                                                            1            2
        item = mediaitem.MediaItem(resultSet[1], htmlentityhelper.HtmlEntityHelper.StripAmp(urlparse.urljoin(self.currentUrlPart, resultSet[0])))
        item.thumb = self.noImage
        item.type = "folder"
        item.complete = True
        item.icon = self.folderIcon
        return item
    
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting FormatVideoItem for %s', self.channelName)
        
        item = mediaitem.MediaItem(resultSet[4].strip(), htmlentityhelper.HtmlEntityHelper.StripAmp(urlparse.urljoin(self.baseUrl, resultSet[0])))
        item.description = "%s" % (resultSet[1],)
        item.thumbUrl = resultSet[2]
        item.type = "video"
        item.complete = False
        item.icon = self.icon
        return item
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. 
        """
        logFile.debug('starting UpdateVideoItem for %s (%s)', item.name, self.channelName)
        
        item.thumb = self.CacheThumb(item.thumbUrl)
        
        # retrieve the mediaurl
        data = uriHandler.Open(item.url, pb=False)
        
        aspxRegex = 'href="([^"]+wmv)"'
        #aspxRegex = 'href="http://[^=]+vurl=([^"]+wmv)"'
        aspxResults = common.DoRegexFindAll(aspxRegex, data)
        asxRegex = '<a href="([^"]+asx)"'
        asxResults = common.DoRegexFindAll(asxRegex, data)
        ramRegex = '<a href="([^"]+ram)">'
        ramResults = common.DoRegexFindAll(ramRegex, data)
        flvRegex = '<param name="flashvars" value="pathflv\W*=\W*([^=$&]+)'
        flvResults = common.DoRegexFindAll(flvRegex, data)
        
        mediaurl = ""
        if len(aspxResults) > 0:
            # first check for ASPX
            logFile.debug("Running WMV %s", aspxResults[0])
            mediaurl = aspxResults[0]
        elif len(asxResults) > 0:
            #then ASX
            logFile.debug("Running ASX")
            mediaurl = "%s%s" % ("http://www.svt.se", asxResults[0])        
        elif len(ramResults) > 0:
            #then RAM
            logFile.debug("Running RAM")
            mediaurl = "%s%s" % ("http://www.svt.se", ramResults[0])
        elif len(flvResults) > 0:
            #then FLV
            logFile.debug("Running FLV")
            mediaurl = flvResults[0]
            if mediaurl.startswith("rtmp"):
                mediaurl = mediaurl.replace("_definst_","?slist=")
            #rtmp://fl1.c00928.cdn.qbrick.com/00928/?slist=/kluster/20090101/090102PASPARET_J53UJH
            #rtmp://fl1.c00928.cdn.qbrick.com/00928/_definst_/kluster/20090101/090102PASPARET_J53UJH
        
        if mediaurl != "":
            item.AppendMediaListItem(mediaurl)            
            item.complete = True            
            logFile.debug("Found mediaurl: %s", item)
        return item


    #============================================================================== 
    def PlayVideoItem(self, item, player="defaultplayer"):
        """ NOT USER EDITABLE
        Accepts an item with or without MediaUrl and playback the item. If no 
        MediaUrl is present, one will be retrieved.
        """
        
        for mediaListItem in item.MediaListItems:
            mediaListItem.Url = self.ReplaceMediaUrl(mediaListItem.Url)
        
        logFile.info("Starting Video Playback of %s using the %s", item, player)
        chn_class.Channel.PlayVideoItem(self, item, player=player)
         
    #==============================================================================
    def ReplaceMediaUrl(self, mediaurl):
        """
            retrieves the real Mediaurl
        """
        # if it is a list, it was already processed. 
        if type(mediaurl) is types.ListType or type(mediaurl) is types.TupleType:
            return mediaurl
        
        elif mediaurl.find(".asx") > 0:
            logFile.debug("Parsing ASX")
            data = uriHandler.Open(mediaurl)
            results = common.DoRegexFindAll('<REF HREF\W*=\W*"([^"]+)"\W*/>', data)
            if len(results) > 0:
                mediaurl = results[0]
            
        elif mediaurl.find(".ram") > 0:
            logFile.debug("Parsing RAM")
            mediaurl = uriHandler.Open(mediaurl)
            mediaurl = mediaurl.split('\n')

        return mediaurl 
        
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def CtMnDownloadItem(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.listItems[selectedIndex] = self.DownloadEpisode(item)

    def CtMnPlayMplayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, "mplayer")
    
    def CtMnPlayDVDPlayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, "dvdplayer")    
    
    #============================================================================== 
    def DownloadEpisode(self, item):
        #check if data is already present and if video or folder
        if item.type == 'folder':
            logFile.warning("Cannot download a folder")
        
        elif item.type == 'video':
            if item.complete == False:
                logFile.info("Fetching MediaUrl for VideoItem")
                item = self.UpdateVideoItem(item)
            
            if not item.HasMediaListItems():
                logFile.error("Cannot determine mediaurl")
                return item
            
            # assume that all items are FLV or not
            if not item.MediaListItems[0].find("flv") > 0:
                dialog = xbmcgui.Dialog()
                dialog.ok(config.appName, "Only FLV items can be downloaded.")
                return item
            else:
                chn_class.Channel.DownloadVideoItem(self, item)            
            return item
        else:
            logFile.warning('Error determining folder/video type of selected item')
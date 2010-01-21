#===============================================================================
# Import the default modules
#===============================================================================
import xbmc, xbmcgui
import re, sys, os
import urlparse
#===============================================================================
# Make global object available
#===============================================================================
import common
import mediaitem
import config
import controls
import contextmenu
import chn_class

logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler

#===============================================================================
# register the channels
#===============================================================================
if (sys.modules.has_key('progwindow')):
    register = sys.modules['progwindow']
elif (sys.modules.has_key('plugin')):
    register = sys.modules['plugin']
#register.channelButtonRegister.append(108)

register.channelRegister.append('chn_sbs6nl.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder, channelCode="sbs")')

#===============================================================================
# main Channel Class
#===============================================================================
class Channel(chn_class.Channel):
    """
    main class from which all channels inherit
    """
    
    #===============================================================================
    def InitialiseVariables(self):
        """
        Used for the initialisation of user defined parameters. All should be 
        present, but can be adjusted
        """
        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self)
        
        self.guid = "0B5163FC-42F4-11DD-84D0-5DFE55D89593"
        self.icon = "sbs6icon.png"
        self.iconLarge = "sbs6large.png"
        self.noImage = "sbs6image.png"
        self.backgroundImage = "background-sbs6.png"
        self.backgroundImage16x9 = "background-sbs6-16x9.png"
        self.channelName = "SBS6"
        self.maxXotVersion = "3.2.0"
        self.channelDescription = "Online uitzendingen van www.SBS6.nl"
        self.sortOrder = 7
        self.moduleName = "chn_sbs6nl.py"
        self.mainListUri = "http://www.sbs6.nl/web/show/id=73863/langid=43"
        self.baseUrl = "http://www.sbs6.nl"
        self.onUpDownUpdateEnabled = True
        
        self.contextMenuItems = []
#        self.contextMenuItems.append(contextmenu.ContextMenuItem("Update Item", "CtMnUpdateItem", itemTypes="video", completeStatus=None))            
#        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
                
        self.requiresLogon = False
        
        #self.episodeItemRegex = '<span class="title"><a  href="([^"]+)"[^>]+>([^<]+)</a></span>' # used for the ParseMainList
        self.episodeItemRegex = '<div class="thumb">\W+<a[^>]+href="(/[^"]+)"[^>]*>\W+<img[^>]+alt="([^"]+)"/>'
        self.videoItemRegex = '<div class="item[^"]*">(\W+<div class="thumb"><[^<]+<img src="([^"]+)" [^>]+></a></div>)*[\W]+<div class="title"><a +href="([^"]+)" [^>]+><span>([^<]+)</span></a></div>[\W]+<div class="airtime"><[^<]+<span>([^<]+)</span></a></div>\W+()*<div class="text"><[^<]+<span>([^<]*)</span></a></div>'   # used for the CreateVideoItem 
        self.pageNavigationRegex = '<a href="([^"]+=)(\d+)"><span>\d+</span></a>' #self.pageNavigationIndicationRegex 
        self.pageNavigationRegexIndex = 1
        
        return True
      
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
#    def CtMnUpdateItem(self, selectedIndex):
#        logFile.debug('Updating item (Called from ContextMenu)')
#        self.onUpDown(ignoreDisabled = True)
#    
#    def CtMnDownloadItem(self, selectedIndex):
#        item = self.listItems[selectedIndex]
#        self.listItems[selectedIndex] = self.DownloadEpisode(item)

    def CtMnPlayMplayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, "mplayer")
    
    def CtMnPlayDVDPlayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item,"dvdplayer")    
    
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateEpisodeItem for %s', self.channelName)
        
        # dummy class
        item = mediaitem.MediaItem(resultSet[1], urlparse.urljoin(self.baseUrl, resultSet[0]))
        item.icon = self.icon
        item.complete = True
        return item
    
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateVideoItem for %s', self.channelName)
        #logFile.debug(resultSet)
        
        item = mediaitem.MediaItem(resultSet[3], urlparse.urljoin(self.baseUrl, resultSet[2]))
        
        item.thumb = self.noImage 
        if (resultSet[0] != ""):
            item.thumbUrl = urlparse.urljoin(self.baseUrl, resultSet[1])
        else:
            item.thumbUrl = ""

        item.date = resultSet[4]
        item.icon = self.icon
        item.description = resultSet[6]                                
        item.type = 'video'
        item.complete = False
        return item
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. Usually retrieves the MediaURL 
        and the Thumb! It should return a completed item. 
        """
        logFile.info('starting UpdateVideoItem for %s (%s)', item.name, self.channelName)
        
        item.thumb = self.CacheThumb(item.thumbUrl)        
        
        # now the mediaurl is derived
        # http://www.garnierstreamingmedia.com/asx/openclip.asp?file=/sbs6/net5/juliastango_S02/juliastango_S02E07.wmv
        #                                             http://asx.sbsnet.nl/net5/juliastango_S02/juliastango_S02E07.wmv
        
        data = uriHandler.Open(item.url, pb=False)
        urls = common.DoRegexFindAll('<a class="wmv-player-holder" href="(http://asx.sbsnet.nl/sbs6/)([^"]+)"></a>', data)
        
        # ASX
        for url in urls:
            mediaurl = "http://www.garnierstreamingmedia.com/asx/openclip.asp?file=/sbs6/sbs6/%s" % (url[1])
        
        # FLV
        if mediaurl == "":
            urls = common.DoRegexFindAll('<a class="flv-player-holder" href="/design/channel/sbs6/swf/mediaplayer.swf\?file=([^"]+)"></a>', data)
            for url in urls:
                mediaurl = url
        
        if mediaurl != "":
            item.AppendMediaListItem(mediaurl)
            item.complete = True
            logFile.debug("Media url was found: %s", item)
        else:
            logFile.debug("Media url was not found.")
        return item    
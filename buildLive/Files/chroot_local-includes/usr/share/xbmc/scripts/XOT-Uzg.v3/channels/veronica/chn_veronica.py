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
register.channelRegister.append('chn_veronica.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder, channelCode="veronica")')

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
        
        self.guid = "01EE94CE-42F4-11DD-89C3-51FD55D89593"
        self.icon = "veronicaicon.png"
        self.iconLarge = "veronicalarge.png"
        self.noImage = "veronicaimage.png"
        self.channelName = "Veronica"
        self.channelDescription = "Uitzendingen op www.veronicatv.nl"
        self.moduleName = "chn_veronica.py"
        self.sortOrder = 8
        self.maxXotVersion = "3.2.0"
        
        self.mainListUri = "http://www.veronicatv.nl/web/show/id=96520/langid=43"
        self.baseUrl = "http://www.veronicatv.nl"
        self.onUpDownUpdateEnabled = True
        
        self.contextMenuItems = []
#        self.contextMenuItems.append(contextmenu.ContextMenuItem("Update Item", "CtMnUpdateItem", itemTypes="video", completeStatus=None))            
#        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
                
        self.requiresLogon = False
        
        self.episodeItemRegex = '<div class="thumb">\W+<a[^>]+href="(/[^"]+)"[^>]*>\W+<img[^>]+alt="([^"]+)"/>' # used for the ParseMainList
        self.videoItemRegex = '<div class="item[^"]*">(\W+<div class="thumb"><[^<]+<img src="([^"]+)" [^>]+></a></div>)*[\W]+<div class="title"><a +href="([^"]+)" [^>]+><span>([^<]+)</span></a></div>[\W]+<div class="airtime"><[^<]+<span>([^<]+)</span></a></div>\W+()*<div class="text"><[^<]+<span>([^<]*)</span></a></div>'   # used for the CreateVideoItem 
        self.pageNavigationRegex = '<a href="([^"]+=)(\d+)"><span>\d+</span></a>' #self.pageNavigationIndicationRegex 
        self.pageNavigationRegexIndex = 1
        
        # decrepated. Using url based on ID now
        #self.mediaUrlRegex = '<param name="src" value="([^"]+)" />'    # used for the UpdateVideoItem
        
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
    def ProcessFolderList(self, url):
        firstTryItems = chn_class.Channel.ProcessFolderList(self, url)
        
        if len(firstTryItems) < 1:
            logFile.debug("No items found, trying alternative method")
            
            #store orginal items
            orgRegex = self.videoItemRegex 
            orgBaseUrl = self.baseUrl
            
            # change the regex, but keep the number of groups identical!
            self.videoItemRegex = '<li[^>]+><img (src=")([^"]+)" [^>]+><a href="([^"]+)">([^<]+)</a>()()()</li>'
            urlSegements  = urlparse.urlparse(url)
            self.baseUrl = "%s://%s" % (urlSegements[0], urlSegements[1])
            altItems = chn_class.Channel.ProcessFolderList(self, url)
            
            # restore orignals
            self.videoItemRegex = orgRegex
            self.baseUrl = orgBaseUrl
            
            return altItems
        else:
            return firstTryItems
        
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
        item.icon = self.icon
         
        if (resultSet[0] != ""):
            item.thumbUrl = urlparse.urljoin(self.baseUrl, resultSet[1])
        else:
            item.thumbUrl = ""

        item.date = resultSet[4]
        item.description = resultSet[6]
        if item.description == "":
            item.description = item.name
            
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
        
        # now the mediaurl is derived. First we try WMV
        data = uriHandler.Open(item.url, pb=False)
        urls = common.DoRegexFindAll('<a class="wmv-player-holder" href="(http://asx.sbsnet.nl)(/[^"]+)"></a>', data)
        
        for url in urls:
            mediaurl = "http://www.garnierstreamingmedia.com/asx/openclip.asp?file=/sbs6%s" % (url[1])
        
        # then we check a different implementation
        if mediaurl == "":
            urls = common.DoRegexFindAll('<param name="url" value="([^"]+)"', data)
            for url in urls:
                mediaurl = url
        
        # and finally a FLV player that is sometimes used
        if mediaurl == "":
            urls = common.DoRegexFindAll('<a class="flv-player-holder" href="[^=]+mediaplayer.swf\?file=([^"]+)">', data)
            for url in urls:
                mediaurl = url
        
        if mediaurl != "":
            item.AppendMediaListItem(mediaurl)
            item.complete = True
            logFile.debug("Media url was found: %s", item)            
        else:
            logFile.debug("Media url was not found.")

        return item    
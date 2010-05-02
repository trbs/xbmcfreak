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
register.channelRegister.append('chn_tvse.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder, channelCode="se6")')
register.channelRegister.append('chn_tvse.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder, channelCode="se3")')
register.channelRegister.append('chn_tvse.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder, channelCode="se8")')
register.channelRegister.append('chn_tvse.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder, channelCode="sesport")')

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
        
        self.baseUrl = "http://viastream.player.mtgnewmedia.se/"
        self.maxXotVersion = "3.2.0"
        self.requiresLogon = False
        self.moduleName = "chn_tvse.py"
                
        if self.channelCode == "se3":
            self.guid = "9EC8F612-2EA4-11DE-867C-B84656D89593"
            #self.mainListUri = "http://viastream.player.mtgnewmedia.se/xml/xmltoplayer.php?type=siteMapData&channel=2se&country=se&category=0"
            self.mainListUri = "http://viastream.viasat.tv/siteMapData/se/2se/0"
            self.icon = "tv3seicon.png"
            self.iconLarge = "tv3selarge.png"
            self.noImage = "tv3seimage.png"
            self.channelName = "TV3"
            self.channelDescription = u'Sända från TV3.se'
        elif self.channelCode =="se6":
            self.guid = "FB34E1F0-2930-11DE-A339-255856D89593"
            #self.mainListUri = "http://viastream.player.mtgnewmedia.se/xml/xmltoplayer.php?type=siteMapData&channel=3se&country=se&category=0"
            self.mainListUri = "http://viastream.viasat.tv/siteMapData/se/3se/0"
            self.icon = "tv6seicon.png"
            self.iconLarge = "tv6selarge.png"
            self.noImage = "tv6seimage.png"
            self.channelName = "TV6"
            self.channelDescription = u'Sända från TV6.se'
        elif self.channelCode =="se8":
            self.guid = "BDC1A5C5-2777-4D05-BB5B-742A88B89CC5"
            #self.mainListUri = "http://viastream.player.mtgnewmedia.se/xml/xmltoplayer.php?type=siteMapData&channel=4se&country=se&category=0"
            self.mainListUri = "http://viastream.viasat.tv/siteMapData/se/4se/0"
            self.icon = "tv8seicon.png"
            self.iconLarge = "tv8selarge.png"
            self.noImage = "tv8seimage.png"
            self.channelName = "TV8"
            self.channelDescription = u'Sända från TV8.se'
        elif self.channelCode == "sesport":
            self.guid = "87533F2C-B759-11DE-A4E3-146355D89593"
            self.mainListUri = "http://viastream.player.mtgnewmedia.se/xml/xmltoplayer.php?type=siteMapData&channel=1se&country=se&category=0"
            self.icon = "sesporticon.png"
            self.iconLarge = "sesportlarge.png"
            self.noImage = "sesportimage.png"
            self.channelName = "Viasat Sport"
            self.channelDescription = u'Sända från viasatsport.se'
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
        
        
        self.episodeItemRegex = '<siteMapNode title="([^"]+)" id="([^"]+)" children="true"'
        self.videoItemRegex = '<ProductId>([^<]+)</ProductId>\W+<Title><!\[CDATA\[([^>]+)\]\]></Title>'
        self.folderItemRegex = '<siteMapNode title="([^"]+)" id="([^"]+)" children="([^"]+)" articles="[123456789]\d*"'
        self.mediaUrlRegex = '<param name="flashvars" value="pathflv\W*=\W*([^"]+)_definst_/([^"]+)\$start'
        
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
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        if self.channelCode == "se8":
            url = "http://viastream.viasat.tv/siteMapData/se/4se/%s" % (resultSet[1],)
        elif self.channelCode == "se6":
            url = "http://viastream.viasat.tv/siteMapData/se/3se/%s" % (resultSet[1],)
        elif self.channelCode == "se3":
            url = "http://viastream.viasat.tv/siteMapData/se/2se/%s" % (resultSet[1],)
        elif self.channelCode == "sesport":
            url = "http://viastream.player.mtgnewmedia.se/xml/xmltoplayer.php?type=siteMapData&channel=1se&country=se&category=%s" %(resultSet[1],)
            
        item = mediaitem.MediaItem(resultSet[0], url)
        item.description = resultSet[0]
        item.icon = self.icon
        return item
    
    #==============================================================================
    def CreateFolderItem(self, resultSet):
        if self.channelCode == "se8" or self.channelCode == "se6" or self.channelCode == "se3":
            url = "http://viastream.viasat.tv/Products/Category/%s" % (resultSet[1],)
        else:
            if resultSet[2] == "false":
                url = "http://viastream.player.mtgnewmedia.se/xml/xmltoplayer.php?type=Products&category=%s" % (resultSet[1],)
            else:        
                url = "http://viastream.player.mtgnewmedia.se/xml/xmltoplayer.php?type=siteMapData&channel=3se&country=se&category=%s" % (resultSet[1],)
            
        item = mediaitem.MediaItem(resultSet[0], url)
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
        
        if (self.channelCode == "sesport"):
            url = "http://viastream.player.mtgnewmedia.se/xml/xmltoplayer.php?type=Products&clipid=%s" % (resultSet[0],)
        else:
            url = "http://viastream.viasat.tv/Products/%s" % (resultSet[0],) #223950

        
        item = mediaitem.MediaItem(resultSet[1], url)
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
        data = uriHandler.Open(item.url, pb=False)
        
        for description in common.DoRegexFindAll("<LongDescription><!\[CDATA\[([^<]+)\]\]", data):
            item.description = description
        
        for image in common.DoRegexFindAll("<Url>([^<]+)</Url>\W+</ImageMedia>", data):
            item.thumbUrl = image        
        item.thumb = self.CacheThumb(item.thumbUrl)
        
        for url in common.DoRegexFindAll("<Url>([^<]+)</Url>\W+</Video>", data):
            item.AppendMediaListItem(url)

        item.complete = True
        logFile.debug("Found mediaurl: %s", item)
        return item
        
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def CtMnPlayMplayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, "mplayer")
    
    def CtMnPlayDVDPlayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, "dvdplayer")    
    
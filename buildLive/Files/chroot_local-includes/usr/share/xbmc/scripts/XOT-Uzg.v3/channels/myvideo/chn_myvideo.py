from uriopener import UriHandler
import uriopener
import xbmc, xbmcgui
import sys, re, urllib, math
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
register.channelRegister.append('chn_myvideo.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder)')

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
        
        self.guid = "A6FF1534-42F3-11DD-8F18-08F555D89593"
        self.mainListUri = "http://www.myvideo.nl/"
        self.baseUrl = "http://www.myvideo.nl"
        self.icon = "myvideoicon.png"
        self.iconLarge = "myvideolarge.png"
        self.noImage = "myvideoimage.png"
        self.channelName = "MyVideo.nl"
        self.channelDescription = "Videos van Myvideo.nl"
        self.moduleName = "chn_myvideo.py"
        self.maxXotVersion = "3.2.0"
        
        #self.backgroundImage = ""
        #self.backgroundImage16x9 = ""
        self.requiresLogon = False
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
        
        
        self.episodeItemRegex = "<a class='nArrow' href='([^']+)' title='[^']*'>([^<]+)</a>"
        self.videoItemRegex = "<img id='([^']+)' src='([^']+)' class='vThumb' alt='[^']*'/></a></div></div><div class='sCenter vTitle'><span class='title'><a[^>]+title='([^']+)'" 
        self.folderItemRegex = ''
        self.mediaUrlRegex = '<item>\W*<file>\W*([^>]*)\W*</file>\W*<bandwidth>(\d+)</bandwidth>'
        
        """ 
            The ProcessPageNavigation method will parse the current data using the pageNavigationRegex. It will
            create a pageItem using the CreatePageItem method. If no CreatePageItem method is in the channel,
            a default one will be created with the number present in the resultset location specified in the 
            pageNavigationRegexIndex and the url from the combined resultset. If that url does not contain http://
            the self.baseUrl will be added. 
        """
        # remove the &amp; from the url
        self.pageNavigationRegex = "<a class='pView pnNumbers'  href='([^?]+\?lpage=)(\d+)([^']+)"  
        self.pageNavigationRegexIndex = 1

        #========================================================================== 
        # non standard items
        self.categoryName = ""
        
        return True
    
    #==============================================================================
    def ParseMainList(self):
        """
            Add some custom categories here
        """
        items = []
        
        item = mediaitem.MediaItem("Nieuwste videos", "http://www.myvideo.nl/news.php?rubrik=rljgs")
        item.icon = self.folderIcon
        items.append(item)
        
        item = mediaitem.MediaItem("Meest bekeken videos", "http://www.myvideo.nl/news.php?rubrik=tjyec")
        item.icon = self.folderIcon
        items.append(item)

        item = mediaitem.MediaItem("Meest besproken videos", "http://www.myvideo.nl/news.php?rubrik=vpjpr")
        item.icon = self.folderIcon
        items.append(item)        
        
        item = mediaitem.MediaItem("Best beoordeelde videos", "http://www.myvideo.nl/news.php?rubrik=xayvg")
        item.icon = self.folderIcon
        items.append(item)        
        
        item = mediaitem.MediaItem("Favoriete videos", "http://www.myvideo.nl/news.php?rubrik=pcvbc")
        item.icon = self.folderIcon
        items.append(item)        
        
        return items + chn_class.Channel.ParseMainList(self)
    
    #============================================================================== 
    def PreProcessFolderList(self, data):
        """
        Accepts an data from the ProcessFolderList Methode, BEFORE the items are
        processed. Allows setting of parameters (like title etc). No return value!
        """
        logFile.info("Performing Pre-Processing")
        _items = []
        
        # extract the category name from the pagedata
        results = common.DoRegexFindAll("in de categorie\W+<span class='[^']+'>[^;]+;([^<]+)&quot", data)
        
        if len(results)> 0:
            self.categoryName = htmlentityhelper.HtmlEntityHelper.ConvertHTMLEntities(results[0])
        
        logFile.debug("Pre-Processing finished")
        return (data, _items)
    
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #logFile.info('starting CreateEpisodeItem for %s', self.channelName)
        #<a class='nArrow' href='([^']+)' title='[^']*'>([^<]+)</a>
        #                            0                     1                                
        item = mediaitem.MediaItem(resultSet[1],htmlentityhelper.HtmlEntityHelper.StripAmp("%s%s" % (self.baseUrl, resultSet[0])))
        item.icon = self.icon
        logFile.debug("%s (%s)", item.name, item.url)
        return item
    
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting FormatVideoItem for %s', self.channelName)
        #<img id='([^']+)' src='([^']+)' class='vThumb' alt='[^']*'/></a></div></div><div class='sCenter vTitle'><span class='title'><a[^>]+title='([^']+)'>
        #            0            1                                                                                                                    2
        name = htmlentityhelper.HtmlEntityHelper.ConvertHTMLEntities(resultSet[2])
        item = mediaitem.MediaItem(name, htmlentityhelper.HtmlEntityHelper.StripAmp("%s%s" % (self.baseUrl, resultSet[0])))
        
        item.description = "%s\n%s" % (self.categoryName, resultSet[2])
        item.icon = self.icon
        item.thumb = self.noImage
        item.thumbUrl = resultSet[1]
        
        # now create the video url using the 
        # http://myvideo-550.vo.llnwd.net/nl/d3/movie7/4a/thumbs/3384551_1.jpg
        # http://myvideo-550.vo.llnwd.net/nl/d3/movie7/4a/3384551.flv
        
        # het script: http://myvideo-906.vo.llnwd.net/nl/d2/movie4/d93548906.flv
        # de pagina:  http://myvideo-906.vo.llnwd.net/nl/d2/movie4/d9/3548906.flv
        
        urlResult = common.DoRegexFindAll("(http://myvideo[^_]+)/thumbs(/\d+)_\d+.jpg", item.thumbUrl)
        mediaurl = ""
        if len(urlResult)>0:
            for part in urlResult[0]:
                mediaurl = "%s%s" % (mediaurl, part)
        mediaurl = "%s.flv" % (mediaurl)
        
        item.AppendMediaListItem(mediaurl)
        logFile.debug("Updated mediaurl for %s", item)
        item.type = 'video'
        item.complete = False
        
        return item
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. 
        """
        logFile.debug('starting UpdateVideoItem for %s (%s)',item.name, self.channelName)
        item.thumb = self.CacheThumb(item.thumbUrl)
        item.complete = True
        return item

    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def CtMnDownloadItem(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.listItems[selectedIndex] = self.DownloadVideoItem(item)

    def CtMnPlayMplayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, "mplayer")
    
    def CtMnPlayDVDPlayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item,"dvdplayer")    
    
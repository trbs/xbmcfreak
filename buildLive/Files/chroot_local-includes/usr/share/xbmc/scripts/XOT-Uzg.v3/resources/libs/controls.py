#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================

#===============================================================================
# Actions
#===============================================================================

ACTION_MOVE_LEFT       =  1
ACTION_MOVE_RIGHT      =  2
ACTION_MOVE_UP         =  3
ACTION_MOVE_DOWN       =  4
ACTION_PAGE_UP         =  5
ACTION_PAGE_DOWN       =  6
ACTION_SELECT_ITEM     =  7
ACTION_HIGHLIGHT_ITEM  =  8
ACTION_PARENT_DIR      =  9
ACTION_PREVIOUS_MENU   = 10
ACTION_SHOW_INFO       = 11
ACTION_PAUSE           = 12
ACTION_STOP            = 13
ACTION_NEXT_ITEM       = 14
ACTION_PREV_ITEM       = 15    
ACTION_CONTEXT_MENU    = 117
ACTION_MOUSE_MOVE      = 90

ACTION_UPDOWN                   = (ACTION_MOVE_UP, ACTION_MOVE_DOWN, ACTION_PAGE_DOWN, ACTION_PAGE_UP)
ACTION_LEFTRIGHT                = (ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT)
ACTION_EXIT_CONTROLS            = (ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR)
ACTION_CONTEXT_MENU_CONTROLS    = (ACTION_CONTEXT_MENU, ACTION_SHOW_INFO)
ACTION_MOUSE_MOVEMENT           = (ACTION_MOUSE_MOVE,)

#===============================================================================
# autoscaling values
#===============================================================================

HDTV_1080i = 0      #(1920x1080, 16:9, pixels are 1:1)
HDTV_720p = 1       #(1280x720, 16:9, pixels are 1:1)
HDTV_480p_4x3 = 2   #(720x480, 4:3, pixels are 4320:4739)
HDTV_480p_16x9 = 3  #(720x480, 16:9, pixels are 5760:4739)
NTSC_4x3 = 4        #(720x480, 4:3, pixels are 4320:4739)
NTSC_16x9 = 5       #(720x480, 16:9, pixels are 5760:4739)
PAL_4x3 = 6         #(720x576, 4:3, pixels are 128:117)
PAL_16x9 = 7        #(720x576, 16:9, pixels are 512:351)
PAL60_4x3 = 8       #(720x480, 4:3, pixels are 4320:4739)
PAL60_16x9 = 9      #(720x480, 16:9, pixels are 5760:4739)    

RESOLUTION_16x9 = (HDTV_1080i, HDTV_720p,  HDTV_480p_16x9, NTSC_16x9, PAL60_16x9, PAL_16x9)
RESOLUTION_4x3 = (HDTV_480p_4x3, NTSC_4x3, PAL60_4x3, PAL_4x3)

#===============================================================================
# control ID's
#===============================================================================
CH_LIST = 51
PR_LIST = 60
EP_LIST = 50     
PG_LIST = 71

PR_LIST_WRAPPER = PR_LIST + 1000
CH_LIST_WRAPPER = CH_LIST + 1000

EP_BACKGROUND = 199
EP_THUMB = 201
EP_COMPLETE = 203
EP_DESCRIPTION = 211
EP_RATING = 220 # till 225

PL_LARGE_ICON = 1001
PL_CHANNEL_NAME = 1002
PL_CHANNEL_DESCRIPTION = 1003 

UD_EXIT = 1002
UD_DESCRIPTION = 1003
UD_LIST = 50





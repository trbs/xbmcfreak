#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================
import unicodedata

class EncodingHelper:
    def __init__(self, decoder = 'utf-8', encoder = 'utf=8'):
        self.decoder = decoder
        self.encoder = encoder

    def Decode(self, data):
        return data.decode(self.decoder, 'replace')
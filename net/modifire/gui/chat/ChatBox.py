from direct.gui.DirectGui import DirectFrame, DirectEntry
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText 
from pandac.PandaModules import TextNode, Vec4, Vec3
from direct.interval.IntervalGlobal import LerpPosInterval

import Settings
import Globals

from event.ChatEvent import ChatOpenEvent, ChatCloseEvent, ChatEnteredEvent
from gui.GUIOrder import GUIOrder

# This class represents the box that players can show to type messages to send to other players
class ChatBox(DirectObject):
    
    MESSAGE_LIFE = 10
    MAX_NUM_MESSAGES = 15
    
    (TYPE_GLOBAL,
     TYPE_TEAM,
     TYPE_CONSOLE) = range(3)
     
    messageTypeToPrefix = { TYPE_GLOBAL : 'Global:', 
                            TYPE_TEAM : 'Team:',
                            TYPE_CONSOLE : 'Console' }
    
    def __init__(self):
        self.textNodes = []
        self.messageType = None
        
        self.rootFrame = DirectFrame(pos = (0.03, 0, 0.2),
                                 frameColor = (0, 0, 0, 0),
                                 frameSize = (0, 1, 0, 1),
                                 parent = base.a2dBottomLeft)
        self.rootFrame.setBin('fixed', GUIOrder.ORDER[GUIOrder.CHAT])
        
        self.entryFrame = DirectFrame(pos = (0, 0, 0),
                                 frameColor = (0, 0, 0, 0.1),
                                 frameSize = (0, 1, 0, 0.1),
                                 parent = self.rootFrame)
        
        self.chatarea = DirectEntry(width = 27,
                                    scale = Settings.CHAT_HEIGHT,
                                    pos = (0, 0, 0),
                                    frameColor = (0, 0, 0, 0),
                                    text_fg = (1, 1, 1, 1),
                                    numLines = 1,
                                    cursorKeys = 1,
                                    rolloverSound = None,
                                    clickSound = None,
                                    focus = 0,
                                    command = self.OnChatEntered,
                                    parent = self.entryFrame)
        
        self.typeText = OnscreenText(text = '', 
                                     pos = (0, Settings.CHAT_HEIGHT + 0.01), 
                                     scale = Settings.CHAT_HEIGHT,
                                     fg = (1, 1, 1, 1),
                                     mayChange = True,
                                     align = TextNode.ALeft,
                                     parent = self.entryFrame)
        
        self.displayFrame = DirectFrame(pos = (0, 0, 0.1),
                                 frameColor = (0, 0, 0, 0),
                                 frameSize = (0, 1, 0, 0.42),
                                 parent = self.rootFrame)
        
        self.chatarea.enterText('')
        self.entryFrame.hide()
        self.chatarea['focus'] = 0
        self.chatarea.setFocus()    
        
    def OnChatEntered(self, enteredText):
        enteredText = enteredText.strip()
        self.Hide()
        if(len(enteredText) > 0):
            ChatEnteredEvent(self.messageType, enteredText).Fire()
        
    def AddMessage(self, prefix, prefixColor, message):
        parent = self.displayFrame.attachNewNode('messageParent')
        
        prefixTextNode = TextNode('prefixMessage')
        prefixTextNode.setText(prefix)
        prefixTextNode.setTextColor(prefixColor)
        prefixTextNode.setShadow(0.05, 0.05)
        prefixTextNode.setShadowColor(Globals.COLOR_BLACK)
        prefixTextNodePath = parent.attachNewNode(prefixTextNode)
        prefixTextNodePath.setScale(Settings.CHAT_HEIGHT)
        
        messageTextNode = TextNode('prefixMessage')
        messageTextNode.setText(message)
        messageTextNode.setTextColor(1, 1, 1, 1)
        messageTextNode.setShadow(0.05, 0.05)
        messageTextNode.setShadowColor(Globals.COLOR_BLACK)
        messageTextNodePath = parent.attachNewNode(messageTextNode)
        messageTextNodePath.setScale(Settings.CHAT_HEIGHT)
        messageTextNodePath.setPos(Vec3(prefixTextNode.calcWidth(prefix) * Settings.CHAT_HEIGHT, 0, 0))
        
        taskMgr.remove('HideMessageLog')
        taskMgr.doMethodLater(ChatBox.MESSAGE_LIFE, self.HideMessageLog, 'HideMessageLog') 
        self.ShowMessageLog()
        
        self.textNodes.append(parent)
        
        if(len(self.textNodes) > ChatBox.MAX_NUM_MESSAGES):
            self.RemoveMessage(self.textNodes[0])
            
        self.RedrawMessages()
        
    def RedrawMessages(self):
        n = len(self.textNodes)
        for i, textNode in enumerate(self.textNodes):
            LerpPosInterval(textNode, 0.5, (0, 0, (n-i) * (Settings.CHAT_HEIGHT + 0.01))).start()
            
    def RemoveMessage(self, textNode):
        self.textNodes.remove(textNode)
        textNode.removeNode()
        
    def HideMessageLog(self, task = None):
        self.displayFrame.hide()
        
    def ShowMessageLog(self):
        self.displayFrame.show()
        
    def Hide(self):
        self.chatarea.enterText('')
        self.entryFrame.hide()
        self.chatarea['focus'] = 0
        self.chatarea.setFocus()
        self.HideMessageLog()
        ChatCloseEvent().Fire()
        
    def Show(self, messageType):
        self.messageType = messageType
        self.entryFrame.show()
        self.chatarea['focus'] = 1
        self.chatarea.setFocus()
        self.typeText.setText(ChatBox.GetPrefix(self.messageType))
        self.ShowMessageLog()
        ChatOpenEvent().Fire()
        
    def EnableKeyboardListening(self):
        self.acceptOnce('escape', self.Hide)
        
    def DisableKeyboardListening(self):
        self.ignoreAll()
        
    @staticmethod
    def GetPrefix(messageType):
        return ChatBox.messageTypeToPrefix[messageType]
    
    def Destroy(self):
        taskMgr.remove('HideMessageLog')
        self.rootFrame.destroy()
        self.entryFrame.destroy()
        self.chatarea.destroy()
        self.typeText.destroy()
        self.displayFrame.destroy()
        self.ignoreAll()
        
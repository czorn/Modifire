from direct.gui.DirectGui import DirectFrame, DirectEntry
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText 
from pandac.PandaModules import TextNode, Vec4, Vec3
from direct.interval.IntervalGlobal import LerpPosInterval

import Settings
import Globals

from event.PlayerEvent import PlayerDeathEvent
from gui.GUIOrder import GUIOrder
from player.PlayerState import PlayerState

# This class represents the box that players can show to type messages to send to other players
class DeathNotifications(DirectObject):
    
    MESSAGE_LIFE = 5
    MAX_NUM_MESSAGES = 10
    
    def __init__(self):
        self.textNodes = []
        
        self.rootFrame = DirectFrame(pos = (-0.05, 0, -0.25),
                                 frameColor = (0, 0, 0, 0),
                                 frameSize = (0, 1, 0, 1),
                                 parent = base.a2dTopRight)
        self.rootFrame.setBin('fixed', GUIOrder.ORDER[GUIOrder.CHAT])
        
        self.displayFrame = DirectFrame(pos = (0, 0, 0),
                                 frameColor = (0, 0, 0, 0),
                                 frameSize = (0, 1, 0, 0.42),
                                 parent = self.rootFrame)   
        
        self.accept(PlayerDeathEvent.EventName, self.OnPlayerDeathEvent)
        
    def OnPlayerDeathEvent(self, event):
        player = event.GetPlayer()
        attacker = event.GetAttacker()
        wasHS = event.WasHeadshot() 
        
        if(not attacker.currentItem):
            itemName = '???'
        else:
            itemName = attacker.currentItem.GetName()
        
        self.AddMessage(victimName = player.GetPlayerState().GetValue(PlayerState.NAME), 
                        attackerName = attacker.GetPlayerState().GetValue(PlayerState.NAME), 
                        itemName = itemName, 
                        attackerColor = Globals.TEAM_COLORS[attacker.GetPlayerState().GetValue(PlayerState.TEAM)], 
                        victimColor = Globals.TEAM_COLORS[player.GetPlayerState().GetValue(PlayerState.TEAM)])
        
    def AddMessage(self, victimName, attackerName, itemName, attackerColor = Globals.COLOR_WHITE, victimColor = Globals.COLOR_WHITE):
        parent = self.displayFrame.attachNewNode('messageParent')
        
        attackerTextNode = TextNode('attackerTextNode')
        attackerTextNode.setText(attackerName)
        attackerTextNode.setTextColor(attackerColor)
        attackerTextNode.setShadow(0.05, 0.05)
        attackerTextNode.setShadowColor(Globals.COLOR_BLACK)
        attackerTextNodePath = parent.attachNewNode(attackerTextNode)
        attackerTextNodePath.setScale(Settings.CHAT_HEIGHT)
        attackerTextNodePath.setPos(Vec3(-attackerTextNode.calcWidth('%s [%s] %s' % (attackerName, itemName, victimName)) * Settings.CHAT_HEIGHT, 0, 0))
        
        itemNameTextNode = TextNode('itemNameTextNode')
        itemNameTextNode.setText('[%s]' % (itemName))
        itemNameTextNode.setTextColor(Globals.COLOR_WHITE)
        itemNameTextNode.setShadow(0.05, 0.05)
        itemNameTextNode.setShadowColor(Globals.COLOR_BLACK)
        itemNameTextNodePath = parent.attachNewNode(itemNameTextNode)
        itemNameTextNodePath.setScale(Settings.CHAT_HEIGHT)
        itemNameTextNodePath.setPos(Vec3(-attackerTextNode.calcWidth('[%s] %s' % (itemName, victimName)) * Settings.CHAT_HEIGHT, 0, 0))
        
        victimTextNode = TextNode('prefixMessage')
        victimTextNode.setText(victimName)
        victimTextNode.setTextColor(victimColor)
        victimTextNode.setShadow(0.05, 0.05)
        victimTextNode.setShadowColor(Globals.COLOR_BLACK)
        victimTextNodePath = parent.attachNewNode(victimTextNode)
        victimTextNodePath.setScale(Settings.CHAT_HEIGHT)
        victimTextNodePath.setPos(Vec3(-attackerTextNode.calcWidth(victimName) * Settings.CHAT_HEIGHT, 0, 0))
        
        taskMgr.remove('HideMessageLog')
        taskMgr.doMethodLater(DeathNotifications.MESSAGE_LIFE, self.RemoveMessage, 'RemoveMessage', extraArgs = [parent]) 
                
        self.textNodes.append(parent)
        
        if(len(self.textNodes) > DeathNotifications.MAX_NUM_MESSAGES):
            self.RemoveMessage(self.textNodes[0])
            
        self.RedrawMessages()
        
    def RedrawMessages(self):
        n = len(self.textNodes)
        for i, textNode in enumerate(self.textNodes):
            LerpPosInterval(textNode, 0.5, (0, 0, -(n-i) * (Settings.CHAT_HEIGHT + 0.01))).start()
            
    def RemoveMessage(self, textNode):
        if(textNode in self.textNodes):
            self.textNodes.remove(textNode)
            textNode.removeNode()
    
    def Destroy(self):
        taskMgr.remove('HideMessageLog')
        self.rootFrame.destroy()
        self.entryFrame.destroy()
        self.chatarea.destroy()
        self.typeText.destroy()
        self.displayFrame.destroy()
        self.ignoreAll()
        
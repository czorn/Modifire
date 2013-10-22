from direct.showbase.DirectObject import DirectObject
from panda3d.core import CollisionNode, CollisionSegment, BitMask32,CollisionSphere, CollisionTube #@UnresolvedImport
from panda3d.core import CollisionTraverser, CollisionHandlerQueue #@UnresolvedImport
from panda3d.core import VBase3, Point3, Vec3 #@UnresolvedImport
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import LerpPosInterval, LerpHprInterval
from direct.filter.CommonFilters import CommonFilters


from item.ItemId import ItemId
from item.Builder import Builder
from item.Firearm import Firearm
from player.PlayerAnimationFSM import PlayerAnimationFSM
from player.PlayerState import PlayerState
from player.InputBuffer import InputBuffer
from player.PositionHistory import PositionHistory
from collision.BoundingBox import BoundingBox
from SelectionGeom import SelectionGeom
from event.PlayerEvent import PlayerSelectedEvent, PlayerReloadEvent
from event.InventoryEvent import SelectedItemChangeEvent, AmmoChangeEvent
from item.ItemStack import ItemStack
from game.Game import Game
from Camera import Camera
from hud.PlayerName import PlayerName
#from PStats import pstat

import Globals
import Settings



class Player(DirectObject):
    
    #----------------
    # Initialization
    #----------------
    
    def __init__(self):
        self.pNode = render.attachNewNode('playerRoot')     # The root node of the player
        self.eyeHeight = 1.5                                # The z height of the camera
        self.selectedBlock = 0
        self.adjacentBlock = 0
        self.selectedPlayer = None
        self.playerState = PlayerState(self)
        self.inputBuffer = InputBuffer()
        self.currentItem = None
        self.itemModels = {}
        self.playerModel = None
        
        # The bounding box of the player for collision with environment geometry
        self.boundingBoxCenterNode = self.pNode.attachNewNode('bboxCenter')
        self.boundingBoxCenterNode.setPos(0, 0, 0.9)
        self.boundingBox = BoundingBox(self.boundingBoxCenterNode, [0.2, 0.2, 0.9])
        
        self.animFSM = PlayerAnimationFSM(self)
        self.animFSM.request('Idle')
        
        self.camNode = self.pNode.attachNewNode('cam')      # The position of the player's eyes
        self.camNode.setPos(0, 0, self.eyeHeight)
        
        self.playerParent = self.pNode.attachNewNode('playerParent')
        
        # Change this back so items follow player turning
        #self.itemNode = self.playerParent.attachNewNode('3rdPersonItem')
        self.itemNode = self.pNode.attachNewNode('3rdPersonItem')
        self.itemNode.setPos(0, 0, 1.2)
        
        self.camItemNode = self.camNode.attachNewNode('1stPersonItem')
        
        # Node for name text
        self.nameText = None
        self.nameNode = self.pNode.attachNewNode('NameNode')
        self.nameNode.setPos(0, 0, 1.97)
        
        self.lookingRayNode = self.pNode.attachNewNode('lookingRayNode')
        self.lookingRayNode.setPos(0, 0, self.eyeHeight)
        
        lookingSeg = CollisionSegment(0, 0, 0, 0, 100, 0)
        self.lookingRay = self.lookingRayNode.attachNewNode(CollisionNode('lookingRay'))
        self.lookingRay.node().addSolid(lookingSeg)
        self.lookingRay.node().setFromCollideMask(Globals.BLOCK_PICKER_BITMASK | Globals.PLAYER_BITMASK)
        self.lookingRay.node().setIntoCollideMask(BitMask32.allOff())
        
        self.lookingRayCollisionEntry = None
        
        self.pickerCollisionHandler = CollisionHandlerQueue()
        self.pickerTraverser = CollisionTraverser('pickerTraverser')
        self.pickerTraverser.addCollider(self.lookingRay, self.pickerCollisionHandler)
        if(not Settings.IS_SERVER):
            self.selectionGeom = SelectionGeom()
        else:
            self.selectionGeom = None
        
        self.CreateCollisionGeoms()
        self.LoadModels()
        
    def CreateCollisionGeoms(self):
        self.collisionNode = self.pNode.attachNewNode('CollisionNode')
        
        collisionGeom = self.collisionNode.attachNewNode(CollisionNode("legsPlayer"))
        collisionGeom.node().addSolid(CollisionSphere(0, 0, 0.35, 0.3))
        collisionGeom.node().setFromCollideMask(Globals.ITEM_BITMASK)
        collisionGeom.node().setIntoCollideMask(Globals.PLAYER_BITMASK)
        #collisionGeom.show()
        collisionGeom.setPythonTag(Globals.TAG_COLLISION, Globals.COLLISION_LEG)
        collisionGeom.setPythonTag(Globals.TAG_PLAYER, self)
        
        collisionGeom = self.collisionNode.attachNewNode(CollisionNode("bodyPlayer"))
        collisionGeom.node().addSolid(CollisionSphere(0, 0, 0.9, 0.3))
        collisionGeom.node().setFromCollideMask(BitMask32.allOff())
        collisionGeom.node().setIntoCollideMask(Globals.PLAYER_BITMASK)
        #collisionGeom.show()
        collisionGeom.setPythonTag(Globals.TAG_COLLISION, Globals.COLLISION_BODY)
        collisionGeom.setPythonTag(Globals.TAG_PLAYER, self)
        
        collisionGeom = self.collisionNode.attachNewNode(CollisionNode("headPlayer"))
        collisionGeom.node().addSolid(CollisionSphere(0, 0, 1.45, 0.35))
        collisionGeom.node().setFromCollideMask(BitMask32.allOff())
        collisionGeom.node().setIntoCollideMask(Globals.PLAYER_BITMASK)
        collisionGeom.setPythonTag(Globals.TAG_COLLISION, Globals.COLLISION_HEAD)
        collisionGeom.setPythonTag(Globals.TAG_PLAYER, self)
        
    def CreateNameTextNode(self, name):
        self.nameText = PlayerName(name, self.nameNode)
        
    def RemoveSelectionGeom(self):
        if(self.selectionGeom is not None):
            self.selectionGeom.Destroy()
            self.selectionGeom = None
        
    def LoadModels(self, teamId = Game.SPECTATE):
        if(self.playerModel is not None):
            self.playerModel.cleanup()
        
        if(teamId == Game.TEAM_1):
            self.playerModel = Actor('Assets/Models/Players/ralph',
                                     {"run":"Assets/Models/Players/ralph-run",
                                      "walk":"Assets/Models/Players/ralph-walk"})
        #elif(teamId == Game.TEAM_2):
        else:
            self.playerModel = Actor('Assets/Models/Players/ralph2',
                                     {"run":"Assets/Models/Players/ralph-run",
                                      "walk":"Assets/Models/Players/ralph-walk"})
        self.playerModel.setScale(0.36)
        self.playerModel.reparentTo(self.playerParent)
        self.playerModel.setH(180)
        #self.playerModel.hide()
        
        self.playerModel.enableBlend() 
        self.playerModel.loop('run')
        self.playerModel.pose('walk', 5)
        
#        self.outlineFilter = CommonFilters(base.win, base.cam)
#        if(not self.outlineFilter.setCartoonInk(0.5)):
#            print 'ERROR CARTOON FILTER'
        
    #--------------------
    # Controlling models
    #--------------------
        
    def HidePlayerModel(self):
        self.playerModel.hide()
        
    def ShowPlayerModel(self):
        self.playerModel.show()
        
    def LoopAnimation(self, animation):
        self.playerModel.setPlayRate(1.0, animation)
        self.playerModel.loop(animation)
        
    def RequestFSMTransition(self, animFSMState):
        self.animFSM.request(animFSMState)
        
    #--------------------
    # Updating
    #--------------------
        
    def Update(self, deltaTime):
        if(self.currentItem):
            self.currentItem.IncreaseTimeSinceLastUse(deltaTime)
                
    def UpdateLookingDirection(self, lookingDirection):
        if(not self.playerModel.isHidden() and self.GetPlayerState().GetValue(PlayerState.PLAYING_STATE) == PlayerState.PS_PLAYING):
            facingDirection = Vec3(lookingDirection.getX(), lookingDirection.getY(), 0)
            facingDirection.normalize()
            self.playerParent.lookAt(Point3(facingDirection))
            self.itemNode.lookAt(Point3(self.itemNode.getPos() + lookingDirection))
            
    def UpdateLookingRayDirection(self, lookingDirection):
        self.lookingRayNode.lookAt(Point3(lookingDirection.getX(), lookingDirection.getY(), lookingDirection.getZ() + self.eyeHeight))
    
    def MovePosToPriorSnapshot(self, numFramesBack):
        self.pNode.setPos(self.GetPlayerState().GetValue(PlayerState.POSITION_HISTORY).GetPosition(numFramesBack))
        
    def ReturnToCurrentPosition(self):
        self.pNode.setPos(self.currentPosition)
    
    #-----------------------
    # Weapons / items
    #-----------------------
    
    def OnSelectedItemChangeEvent(self, event):
        if(event.GetItemStack()):
            self.ChangeItem(event.GetItemStack().GetItem())
        else:
            self.ChangeItem(None)
        
    def ChangeItem(self, item):
        print 'CHANGE ITEM curr', self.currentItem, 'new', item, self.GetPlayerState().GetValue(PlayerState.PID)
        
#        if(self.currentItem):
#            self.playerState.UpdateValue(PlayerState.CURRENT_ITEM, self.currentItem.GetItemId())
#        else:
#            self.playerState.UpdateValue(PlayerState.CURRENT_ITEM, ItemId.NoItem)
        
        if(item != self.currentItem):
        
            oldItem = self.currentItem
            self.currentItem = item
                
            if(self.currentItem):
                self.playerState.UpdateValue(PlayerState.CURRENT_ITEM, self.currentItem.GetItemId())
            else:
                self.playerState.UpdateValue(PlayerState.CURRENT_ITEM, ItemId.NoItem)
                
            
            #If both are item objects, equip dequip
            if(self.currentItem and oldItem):
                if(not Settings.IS_SERVER):
                    self.currentItem.LoadContent()
                    self.currentItem.ReparentTo(self.camItemNode)
                self.currentItem.EquipDequip(oldItem)
                
            
            # If just the old item is an obj, dequip it
            elif(oldItem):
                oldItem.Dequip()
                
            # If just the new item is an obj, equip it
            elif(self.currentItem):
                if(not Settings.IS_SERVER):
                    self.currentItem.LoadContent()
                    self.currentItem.ReparentTo(self.camItemNode)
                self.currentItem.Equip()
            
    # Change the item as though this is ourself, but then
    # reparent it so that it shows up properly in 3rd person
    def ThirdPersonChangeItem(self, item):
        self.ChangeItem(item)
        if(item and not Settings.IS_SERVER):
            self.currentItem.ReparentTo(self.itemNode)
            
    def ChangeBlockToPlace(self, direction):
        if(isinstance(self.currentItem, Builder)):
            if(direction > 0):
                self.currentItem.IncreaseBlock()
            else:
                self.currentItem.DecreaseBlock()
                
    def Reload(self):
        if(isinstance(self.currentItem, Firearm)):
            self.currentItem.Reload()
            
            # If we reloaded, tell fire an event
            if(self.GetPlayerState().GetValue(PlayerState.PID) == Globals.MY_PID):
                PlayerReloadEvent(self).Fire()
                
    def OnTeamChange(self, teamId):
        self.GetPlayerState().UpdateValue(PlayerState.TEAM, teamId)
        self.LoadModels(teamId)
        if(self.GetPlayerState().GetValue(PlayerState.PID) == Globals.MY_PID):
            self.HidePlayerModel()
        else:  
            if(teamId != Globals.MY_TEAM):
                self.nameText.reshowOnInView = False
                self.nameText.Hide()
                
            else:
                self.nameText.reshowOnInView = True
                self.ShowNameAboveHead()
                
            self.nameText.SetColor(Globals.TEAM_COLORS[teamId])
        
        #self.nameTextNode.setTextColor(Globals.TEAM_COLORS[teamId])
        
    #------------------
    # Death / Respawn
    #-------------------
    
    def OnDeath(self):
        self.collisionNode.stash()
        LerpHprInterval(self.playerParent, 0.7, (self.playerParent.getH(), 90, self.playerParent.getR())).start()
        self.itemNode.hide()
        self.camItemNode.hide()
        self.GetPlayerState().UpdateValue(PlayerState.PLAYING_STATE, PlayerState.PS_PLAYING_DEAD)
        
        # If this is the actual player
        if(self.GetPlayerState().GetValue(PlayerState.PID) == Globals.MY_PID):
            self.ShowPlayerModel()
            if(isinstance(self.currentItem, Firearm) and self.currentItem.IsADS()):
                self.currentItem.ToggleADS()
        
    def OnRespawn(self):
        self.collisionNode.unstash()
        self.GetInputBuffer().Clear()
        self.itemNode.show()
        self.camItemNode.show()
        self.GetPlayerState().UpdateValue(PlayerState.PLAYING_STATE, PlayerState.PS_PLAYING)
        
        if(self.GetPlayerState().GetValue(PlayerState.PID) == Globals.MY_PID):
            print 'Respawn event for me'
            self.HidePlayerModel()
            SelectedItemChangeEvent(None, ItemStack(self.currentItem)).Fire()
            
        else:
            self.ShowPlayerModel()
            
    #----------------------
    # Accessor / Mutators
    #----------------------
        
    def GetPos(self):
        return self.pNode.getPos()
    
    def SetPos(self, value):
        self.pNode.setPos(value)
        
    def GetZ(self):
        return self.pNode.getZ()
        
    def LerpTo(self, pos):
        LerpPosInterval(self.pNode, 0.1, pos).start()
        
    #---------------------------------------
    # Playernames on screen
    #---------------------------------------
    
    def ShowNameAboveHead(self):
        self.nameText.Show()
        
    def FadeOutNameAboveHead(self, task = None):
        self.nameText.FadeOut()
        
    #---------------------------------------
    # Picking things with looking direction
    #----------------------------------------
        
    #@pstat
    def PerfromLookingRayCollision(self, isSelf = True):
        self.pickerTraverser.traverse(render)
        
        entries = []
        for i in range(self.pickerCollisionHandler.getNumEntries()):
            entry = self.pickerCollisionHandler.getEntry(i)
            entries.append(entry)
            
        numEntries = len(entries)
        
        if(numEntries > 0):
            entries.sort(lambda x,y: cmp(self.DistanceFromCam(x.getSurfacePoint(render)),
                                         self.DistanceFromCam(y.getSurfacePoint(render))))
            
            self.lookingRayCollisionEntry = None
            playerEntry = None
            blockCollisionEntry = None
            
            for i in xrange(numEntries):
                if(entries[i].getIntoNodePath().getParent() != self.collisionNode):
                    target = entries[i].getIntoNodePath().__str__()
                    if(target.endswith('blockCollision')):
                        blockCollisionEntry = entries[i]
                        self.lookingRayCollisionEntry = blockCollisionEntry
                        break
                    elif(target.endswith('Player')):
                        playerEntry = entries[i]
                        self.lookingRayCollisionEntry = playerEntry
                        break
            
            if(blockCollisionEntry and isinstance(self.currentItem, Builder)):
                point = blockCollisionEntry.getSurfacePoint(render)
                
                if(self.DistanceFromCam(point) <= Globals.MAX_SELECT_DISTANCE):
                    
                    norm = blockCollisionEntry.getSurfaceNormal(render)
                    self.adjacentBlock = point + norm * 0.2
                    point -=  norm * 0.2
                    
                    x = point.getX()
                    y = point.getY()
                    z = point.getZ()
                    
                    if(self.selectionGeom):
                        self.selectionGeom.SetPos(int(x), int(y), int(z))
                        self.selectionGeom.Show()
                        self.selectedBlock = self.selectionGeom.GetPos() 
                    else:
                        self.selectedBlock = VBase3(int(x), int(y), int(z))
                else:
                    self.selectedBlock = None
                    self.adjacentBlock = None
                    if(self.selectionGeom):
                        self.selectionGeom.Hide()                
            else:
                self.selectedBlock = None
                self.adjacentBlock = None
                if(self.selectionGeom):
                    self.selectionGeom.Hide()
            
            if(playerEntry):
                player = playerEntry.getIntoNodePath().getPythonTag(Globals.TAG_PLAYER)
                if(player):
                    # Each frame, if the crosshairs are hovering a player, fire the event
                    # so the HUD can respond.
                    PlayerSelectedEvent(player).Fire()
                    self.selectedPlayer = player
                    
#                    # Before, we were only firing on changes
#                    if(self.selectedPlayer != player):
#                        self.selectedPlayer = player
#                        if(not Settings.IS_SERVER and isSelf):
#                            PlayerSelectedEvent(player).Fire()
                            
            else:
                if(self.selectedPlayer != None):
                    self.selectedPlayer = None
                    if(not Settings.IS_SERVER and isSelf):
                        PlayerSelectedEvent(None).Fire()
                
    def DistanceFromCam(self, otherPoint):
        eye = self.camNode.getPos(render)
        return (otherPoint - eye).length()
    
    def GetSelectedBlock(self):
        return self.selectedBlock
    
    def GetAdjacentBlock(self):
        return self.adjacentBlock
    
    def GetPlayerState(self):
        return self.playerState
    
    def GetInputBuffer(self):
        return self.inputBuffer
    
    def GetPlayerOverheadName(self):
        return self.nameText
    
    def GetCurrentItem(self):
        return self.currentItem
        
    #---------------
    # Cleanup
    #---------------
    
    def Destroy(self):
        for child in self.pNode.getChildren():
            child.removeNode()
        self.pNode.removeNode()
        if(self.playerModel):
            self.playerModel.delete()
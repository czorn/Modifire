#from direct.showbase.DirectObject import DirectObject
#from panda3d.core import VBase3, CollisionHandlerQueue, CollisionTraverser
#
#from inworldentities.ItemInWorld import ItemInWorld
#from inventory.items.ItemType import ItemType
#
#class ItemInWorldController(DirectObject):
#    
#    itemTypeToModelString ={ItemType.SMGBase : 'SMGBase', 
#                            ItemType.RifleBase : 'RifleBase',
#                            ItemType.SniperBase : 'SniperBase',
#                            
#                            ItemType.Rifle_Auto : 'Rifle_Auto',
#                            ItemType.Rifle_Burst : 'Rifle_Burst',
#                            ItemType.Rifle_Semi : 'Rifle_Semi',
#                            
#                            ItemType.SMG_Auto : 'SMG_Auto',
#                            
#                            ItemType.Sniper_Bolt : 'Sniper_Bolt',
#                            ItemType.Sniper_Semi : 'Sniper_Semi',
#                            
#                            ItemType.MidMetal : 'MidMetal',
#                            ItemType.LowMetal : 'LowMetal',
#                            ItemType.HighMetal : 'HighMetal'}
#    
#    def __init__(self, game, playerSphere):
#        self.game = game
#        self.items = {}
#        self.index = 0
#        self.itemTraverser = CollisionTraverser('itemTraverser')
#        self.itemCollisionHandler = CollisionHandlerQueue()
#        self.itemTraverser.addCollider(playerSphere, self.itemCollisionHandler)
#        self.PutModelsInMemory()
#        
#    def PutModelsInMemory(self):
#        for k, v in ItemInWorldController.itemTypeToModelString.iteritems():
#            loader.loadModel("Assets/Models/Items/%s" % (v), callback = self.ModelLoadedCallback)
#            
#    def ModelLoadedCallback(self, model):
#        pass
#        
#    def Update(self, deltaTime, blocks):
#        for k, item in self.items.iteritems():
#            item.UpdatePos(deltaTime)
#            self.ItemCollisionWithEnvironment(item, blocks)
#            
#        self.itemTraverser.traverse(render)
#        
#        for i in range(self.itemCollisionHandler.getNumEntries()):
#            entry = self.itemCollisionHandler.getEntry(i)
#            itemSphere = entry.getIntoNode()
#            itemTag = itemSphere.getTag('item')
#            item = self.items[itemTag]
#            messenger.send('itemPickUp', [item])
#            #self.game.OnItemPickUp(item)
#            item.Destroy()
#            del self.items[itemTag]
#            
#    def ItemCollisionWithEnvironment(self, item, blocks):
#        pos = item.GetPos()
#        x = pos.getX()
#        y = pos.getY()
#        z = pos.getZ()
#        
#        x1 = int(x)
#        y1 = int(y)
#        z1 = int(z)
#        
#        if(z1 < 0):
#            z1 = 0
#            
#        #if( not self.environment.AreValidIndices(x1, y1, z1)):
#        #    return
#        
#        if(blocks[x1][y1][z1].IsSolid()):
#            item.SetPos(VBase3(x, y, (z1 + 1)))
#            item.velocity = VBase3(0, 0, 0)
#            item.timeElapsed = 0
#        
#    def TossItem(self, itemType, direction, pos):
#        item = ItemInWorld(itemType, ItemInWorldController.itemTypeToModelString[itemType], str(self.index))
#        item.velocity = direction * 3
#        self.AddItem(item, pos)
#        self.index += 1
#        
#    def AddItem(self, item, position):
#        self.items[str(self.index)] = item
#        item.SetPos(position)
#        item.StartSpin()
#    
#    def RemoveItem(self, item):
#        item.StopSpin()
#        self.items.remove(item)
#        item.Destroy()
#        
#    def Destroy(self):
#        pass
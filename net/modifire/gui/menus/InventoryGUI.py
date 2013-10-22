from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib
from panda3d.core import VBase3

from gui.GUIOrder import GUIOrder

from gui.menus.Menu import Menu
from gui.FireModeButton import FireModeButton
from gui.InventorySlotButton import InventorySlotButton
from inventory.MainInventory import MainInventory
from inventory.Inventory import Inventory
from item.SMGAuto import SMGAuto
from item.RifleAuto import RifleAuto
from item.ItemStack import ItemStack
from item.Weapon import Weapon

import Globals

class InventoryGUI(Menu):
    
    def __init__(self, mainInventory):
        Menu.__init__(self)
        self.mainInventory = mainInventory
        self.itemComponentInventory = Inventory(3, 1)
        self.itemResultInventory = Inventory(3, 1)
        self.weaponCraftInventory = Inventory(3, 1)
        self.topAttachmentInventory = Inventory(1, 1)
        self.bottomAttachmentInventory = Inventory(1, 1)
        self.frontAttachmentInventory = Inventory(1, 1)
        #self.node = aspect2d.attachNewNode('Inventory GUI', sort = 0)#GUIOrder.ORDER[GUIOrder.HUD])
        self.inventories = [self.mainInventory, 
                            self.itemComponentInventory, 
                            self.itemResultInventory, 
                            self.weaponCraftInventory, 
                            self.topAttachmentInventory, 
                            self.bottomAttachmentInventory, 
                            self.frontAttachmentInventory]
        self.selectedItemStack = None
        
        self.LoadContent()
        
    def Update(self):
        for inventory in self.inventories:
            if(inventory.IsDirty()):
                self.UpdateIcons(inventory)
                inventory.SetDirty(False)
                
        if(self.selectedItemStack is not None):
            mousePos = Globals.GetAspect2DMousePos()
            self.selectedItemStack.GetItem().GetItemIcon().SetPos(VBase3(mousePos[0], 0, mousePos[1]))            
                
    def UpdateIcons(self, inventory):
        itemStacks = inventory.GetItemStacks()
        for itemStack in itemStacks:
            item = itemStack.GetItem()
            item.LoadIcon(self.node)
            itemIcon = item.GetItemIcon()
            parentSlots = itemStack.GetParentSlots()
            
            # Average the positions of the slots the itemstack belongs to
            pos = VBase3(0, 0, 0)
            numSlots = 0
            for parentSlot in parentSlots:
                numSlots += 1
                pos += parentSlot.GetInventorySlotButton().GetPos()
            pos /= 1.0 * numSlots
            itemIcon.SetPos(pos)
        
    def LoadContent(self):
        # Load the dark background
        blackBG = OnscreenImage(image = 'Assets/Images/Inventory/BlackScreen.png', scale = (2, 1, 1))
        blackBG.setTransparency(TransparencyAttrib.MAlpha)
        blackBG.reparentTo(self.node)
        
        # Load the inventory image
        self.inventoryBackground = OnscreenImage(image = 'Assets/Images/Inventory/inventory.png')
        self.inventoryBackground.setTransparency(TransparencyAttrib.MAlpha)
        self.inventoryBackground.reparentTo(self.node)    
        
        # Load the button for changing the firemode
        self.fmButton = FireModeButton(self.node)
        
        # Load the inventory slots
        startPos = [[263, 524], [622, 440], [622, 282], [372, 361], [406, 282], [406, 440], [293, 361]]
        padding = 69
        for i, inventory in enumerate(self.inventories):
            invSlots = inventory.GetInventorySlots()
            for x in xrange(len(invSlots)):
                for y in xrange(len(invSlots[0])):
                    inventorySlot = invSlots[x][y]
                    if(isinstance(inventory, MainInventory)):
                        if(y == 0):
                            button = InventorySlotButton(x, y, startPos[i][0], 741, padding, x, 0, inventorySlot, inventory, self.OnInventorySlotButtonClick)
                        else:
                            button = InventorySlotButton(x, y, startPos[i][0], startPos[i][1], padding, x, y - 1, inventorySlot, inventory, self.OnInventorySlotButtonClick)
                    else:
                        button = InventorySlotButton(x, y, startPos[i][0], startPos[i][1], padding, x, y, inventorySlot, inventory, self.OnInventorySlotButtonClick)
                    button.ReparentTo(self.node)
                    inventorySlot.SetInventorySlotButton(button)
                    
        self.node.hide()
        
    def Show(self):
        self.node.show()
        
    def Hide(self):
        self.node.hide()
        
    def CheckItemComponentInventoryForCompletion(self):
        items = [x.GetItem() for x in self.itemComponentInventory.GetItemStacks()]
        itemClasses = sorted([x.__class__ for x in items])
        for item in items:
            for possibleItem in item.GetPossibleItems():
                obj = possibleItem()
                if(sorted(obj.GetRecipe()) == itemClasses):
                    print 'created', obj
                    obj.LoadIcon(self.node)
                    self.itemResultInventory.AddItemStack(ItemStack(obj))
                    return
                else:
                    obj.Destroy()
                    del obj
        
    def PreviewOnItemStackPickedUp(self, itemStack, inventory):
        if(inventory == self.weaponCraftInventory):
            item = itemStack.GetItem()
            indices = inventory.GetIndices(itemStack)
            fm = self.fmButton.GetMode()
            result = item.GetWeapon(fm)
            if(result is not None):
                inventory.Clear()
                item = result()
                item.LoadIcon(self.node)
                inventory.PlaceItemStack(ItemStack(item), indices[0], indices[1])
                
        if(inventory == self.itemComponentInventory):
            self.itemResultInventory.Clear()
            self.CheckItemComponentInventoryForCompletion()
            
    def OnItemStackPickedUp(self, itemStack, inventory):
        itemStack.GetItem().GetItemIcon().setBin('fixed', GUIOrder.ORDER[GUIOrder.INV_HIGH])
        
        if(inventory == self.itemComponentInventory):
            self.itemResultInventory.Clear()
            self.CheckItemComponentInventoryForCompletion()
            
        if(inventory == self.itemResultInventory):
            self.itemComponentInventory.Clear()
        
    def OnItemStackPlaced(self, itemStack, inventory):  
        itemStack.GetItem().GetItemIcon().setBin('fixed', GUIOrder.ORDER[GUIOrder.INV_LOW])
              
        if(inventory == self.weaponCraftInventory):
            weapon = itemStack.GetItem()
            if(isinstance(weapon, Weapon)):
                fm = weapon.GetFireMode()
                baseWeapon = weapon.GetBaseWeapon()
                if(baseWeapon is not None):
                    inventory.Clear()
                    item = baseWeapon()
                    
                    if(inventory.AddItemStack(ItemStack(item))):
                        item.LoadIcon(self.node)
                        
                    self.fmButton.SetMode(fm)
                    
        elif(inventory == self.itemResultInventory):
            item = itemStack.GetItem()
            for component in item.GetRecipe():
                item = component()
                item.LoadIcon(self.node)
                self.itemComponentInventory.AddItemStack(ItemStack(item))
        
        elif(inventory == self.itemComponentInventory):
            print itemStack.GetItem()
            self.itemResultInventory.Clear()
            self.CheckItemComponentInventoryForCompletion()
                    
    def OnInventorySlotButtonClick(self, invSlotButton):
        parentInventory = invSlotButton.GetParentInventory()
        
        inventorySlot = invSlotButton.GetInventorySlot()
        itemStackAtSlot = inventorySlot.GetItemStack()
        
        if(itemStackAtSlot is None):
            if(self.selectedItemStack):
                if(self.CanPlaceItem(parentInventory)):
                    indices = invSlotButton.GetSlotIndices()
                    x = indices[0]
                    y = indices[1]
                    dx = 0
                    itemWidth = self.selectedItemStack.GetItem().GetItemWidth()
                    if(itemWidth > 2):
                        dx = 2 - itemWidth
                        x += dx
                        if(x < 0):
                            x = 0
                        
                    if(parentInventory.PlaceItemStack(self.selectedItemStack, x, y)):
                        self.OnItemStackPlaced(self.selectedItemStack, parentInventory)
                        self.selectedItemStack = None
                    else:
                        if(dx > 0 and parentInventory.PlaceItemStack(self.selectedItemStack, x+ 1, y)):
                            self.OnItemStackPlaced(self.selectedItemStack, parentInventory)
                            self.selectedItemStack = None
                        
        else:
            if(self.selectedItemStack is None):
                indices = invSlotButton.GetSlotIndices()
                print 'picking up', itemStackAtSlot.GetItem()
                self.PreviewOnItemStackPickedUp(itemStackAtSlot, parentInventory)
                self.selectedItemStack = parentInventory.GetItemStack(indices[0], indices[1])
                parentInventory.RemoveItemStack(indices[0], indices[1])
                self.OnItemStackPickedUp(self.selectedItemStack, parentInventory)
                
        
    def CanPlaceItem(self, inventory):
        if(inventory == self.itemResultInventory and (not self.itemComponentInventory.IsEmpty() or not self.itemResultInventory.IsEmpty())):
            return False
        
        if(inventory == self.weaponCraftInventory and (not self.weaponCraftInventory.IsEmpty())):
            return False
        
        return True
    
    def Destroy(self):
        for inventory in self.inventories:
            inventory.Destroy()
            del inventory
        self.node.removeNode()
        del self.node
        
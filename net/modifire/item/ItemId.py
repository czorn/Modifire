

class ItemId():
    
    (Unknown,
     NoItem,
     Builder,
     LowMetal,
     MidMetal,
     Pickaxe,
     RifleAuto,
     RifleBase,
     RifleBurst,
     RifleSemi,
     SMGAuto,
     SMGBase,
     SniperBase,
     SniperBolt,
     SniperSemi) = range(15)
     
    toItem = None
    
    @staticmethod
    def ToItem(itemId):
        if(ItemId.toItem == None):
            print 'toItem is none'
            from item.Builder import Builder
            from item.LowMetal import LowMetal
            from item.MidMetal import MidMetal
            from item.Pickaxe import Pickaxe
            from item.RifleAuto import RifleAuto
            from item.RifleBase import RifleBase
            from item.RifleBurst import RifleBurst
            from item.RifleSemi import RifleSemi
            from item.SMGAuto import SMGAuto
            from item.SMGBase import SMGBase
            from item.SniperBase import SniperBase
            from item.SniperBolt import SniperBolt
            from item.SniperSemi import SniperSemi
            
            ItemId.toItem ={ItemId.Unknown : None,
                            ItemId.NoItem : None,
                            ItemId.Builder : Builder,
                            ItemId.LowMetal : LowMetal,
                            ItemId.MidMetal : MidMetal,
                            ItemId.Pickaxe : Pickaxe,
                            ItemId.RifleAuto : RifleAuto,
                            ItemId.RifleBase : RifleBase,
                            ItemId.RifleBurst : RifleBurst,
                            ItemId.RifleSemi : RifleSemi,
                            ItemId.SMGAuto : SMGAuto,
                            ItemId.SMGBase : SMGBase,
                            ItemId.SniperBase : SniperBase,
                            ItemId.SniperBolt : SniperBolt,
                            ItemId.SniperSemi : SniperSemi }
            
        return ItemId.toItem[itemId]
from direct.directbase import DirectStart
from direct.filter.CommonFilters import CommonFilters

from pandac.PandaModules import loadPrcFileData
loadPrcFileData('', 'sync-video 0')

ralph = loader.loadModel('Assets/Models/Items/SMGAuto')
ralph.reparentTo(render)

shader = loader.loadShader('Assets/Shaders/myOutline.sha')
ralph.setShader(shader)

run()
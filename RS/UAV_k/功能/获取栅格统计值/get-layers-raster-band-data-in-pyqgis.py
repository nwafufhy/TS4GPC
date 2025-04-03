# 参考文献：https://gis.stackexchange.com/questions/331097/get-layers-raster-band-data-in-pyqgis

# Here is a function to convert a QgsRasterLayer to a numpy array without GDAL 
# through using the block method of the QgsRasterDataProvider(link):

from numpy import array

def convertRasterToNumpyArray(lyr): #Input: QgsRasterLayer
    values=[]
    provider= lyr.dataProvider()
    block = provider.block(1,lyr.extent(),lyr.width(),lyr.height())
    for i in range(lyr.height()):
        for j in range(lyr.width()):
            values.append(block.value(i,j))
    return array(values)

lyr = iface.mapCanvas().layers()[0]

print(convertRasterToNumpyArray(lyr))
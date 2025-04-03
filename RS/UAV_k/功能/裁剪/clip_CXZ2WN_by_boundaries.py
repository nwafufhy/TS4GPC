import os

path_CXZ_raster = r'D:\work\CXZ-WN\CXZ-WN-2023\CXZ-WN-230408\bule.data.tif'
path_boundaries_shp = r'D:\work\CXZ-WN\CXZ-WN-2023\boundaries\boundaries.shp'

CLIP = path_boundaries_shp
inRaster = path_CXZ_raster
outRaster = r'D:\work\CXZ-WN\CXZ-WN-2023\CXZ-WN-230408\clip_blue.tif'

# cmd = f'gdalwarp -q -cutline {clip_shapefile} -crop_to_cutline {raster_path} {output_path}'
cmd = 'gdalwarp -q -cutline %s -crop_to_cutline %s %s' % (CLIP, inRaster, outRaster)
os.system(cmd)

### 测试
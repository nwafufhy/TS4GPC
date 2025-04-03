import os


path_folder = r"D:\work\CXZ-WN\WN_2024_origin\WN-240130"
path_raster = os.path.join(path_folder,'正射影像镶嵌图.data.tif')
output_path = os.path.join(path_folder,'single.tif')

cmd = f'gdal_translate -b 1 {path_raster} {output_path}'
try:
    os.system(cmd)
    print(f"Processed {path_raster} to {output_path}")
except Exception as e:
    print(f"Error processing {path_raster}: {e}")
import os

def get_tif_files(directory):
    if not os.path.exists(directory):
        raise FileNotFoundError(f"目录不存在: {directory}")
    tif_files = []
    # 遍历指定目录及其子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 检查文件扩展名是否为 .tif
            if file.endswith('.tif'):
                # 构建文件的完整路径
                file_path = os.path.join(root, file)
                tif_files.append(file_path)
    return tif_files

def get_list_time_band(tif_files):
    time_list = []
    band_list = []

    for path in tif_files:
        # 提取时间信息
        parts = path.split(os.sep)
        # print(parts)
        for part in parts:
            if "CXZ-WN-" in part and len(part) > 11:
                # print(part)
                time_info = part.split("-")[-1]
                # print(time_info)
                time_list.append(time_info)
                break
        # 提取波段信息
        file_name = os.path.basename(path)
        band_info = os.path.splitext(file_name)[0]
        band_list.append(band_info)

    # 去重并排序
    time_list = sorted(set(time_list))
    band_list = sorted(set(band_list))

    return time_list,band_list

if __name__ == "__main__":
    base_path = r"D:\work\DATA\DATA_TS4GPC\raw\UAV\CXZ-WN\CXZ-WN-2024"
    # 获取并打印所有图像路径
    tif_files = get_tif_files(base_path)

    # 打印所有 .tif 文件的完整路径
    # for file_path in tif_files:
    #     print(file_path)

    # 获取时间列表和波段列表
    time_list,band_list = get_list_time_band(tif_files)

    print("时间列表:", time_list)
    print("波段列表:", band_list)


   


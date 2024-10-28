import subprocess
import os

###
### copy file
###
# 设置主路径
main_path = '/home/liyin/DATA_LL/ds004199-download/'  # 替换为你的路径
sapath = '/home/liyin/DATA_LL/FCD_MNI/FCD_2/'

# 遍历主路径下的所有子文件夹
for folder in os.listdir(main_path):
    
    print(folder)
    
    if 'sub' not in folder:
        continue
    
    # 如果输出文件夹不存在，则创建它
    os.makedirs(os.path.join(sapath, folder), exist_ok=True)
    
    files = os.listdir(os.path.join(main_path, folder, 'anat'))
    
    for file in files:
        if file.endswith('T1w.nii.gz'):
            # 读取 NIfTI 文件
            file_path = os.path.join(main_path, folder, 'anat', file)
            img = nib.load(file_path)

            # 获取空间分辨率
            hdr = img.header
            spacing = hdr.get_zooms()  # 获取每个维度的分辨率

            #print(f'File: {file_path}')
            print(f'Spatial Resolution: {spacing}')

            shutil.copy2(file_path, sapath+'/T1.nii.gz')

        if file.endswith('FLAIR.nii.gz'):
            # 读取 NIfTI 文件
            file_path = os.path.join(main_path, folder, 'anat', file)
            img = nib.load(file_path)

            # 获取空间分辨率
            hdr = img.header
            spacing = hdr.get_zooms()  # 获取每个维度的分辨率

            #print(f'File: {file_path}')
            print(f'Spatial Resolution: {spacing}')

            shutil.copy2(file_path, sapath+'/FLAIR.nii.gz')

        if file.endswith('FLAIR_roi.nii.gz'):
            # 读取 NIfTI 文件
            file_path = os.path.join(main_path, folder, 'anat', file)
            img = nib.load(file_path)

            # 获取空间分辨率
            hdr = img.header
            spacing = hdr.get_zooms()  # 获取每个维度的分辨率

            #print(f'File: {file_path}')
            print(f'Spatial Resolution: {spacing}')

            shutil.copy2(file_path, sapath+'/mask.nii.gz')
        


# 获取文件夹列表，去除非文件夹元素，并保留完整路径
data_dir_path = '/home/liyin/DATA_LL/FCD_MNI/FCD_2/'
data_dirs = [os.path.join(data_dir_path, d) for d in os.listdir(data_dir_path) if os.path.isdir(os.path.join(data_dir_path, d))]

print(data_dirs)  # 打印文件夹列表

# 定义错误日志文件
error_log_path = 'error_log.txt'

for index,data_dir in enumerate(data_dirs):
    print(index,len(data_dirs),data_dir)
    try:
        # 设置输入文件路径
        t1_image = os.path.join(data_dir, 'T1.nii')
        flair_image = os.path.join(data_dir, 'FLAIR.nii')
        #pet_image = os.path.join(data_dir, 'PET.nii')
        #mask_image = os.path.join(data_dir, 'mask.nii')

        # 设置输出文件路径
        subject_id = os.path.basename(data_dir)  # 使用文件夹名作为 subject_id
        subjects_dir = os.environ['SUBJECTS_DIR']
        output_dir = os.path.join(subjects_dir, subject_id)

        # 确保输出文件夹存在
        os.makedirs(output_dir, exist_ok=True)

        # 准备数据：转换为 FreeSurfer 格式
        convert_to_freesurfer_format(t1_image, 'T1.mgz')
        convert_to_freesurfer_format(flair_image, 'FLAIR.mgz')
        #convert_to_freesurfer_format(pet_image, 'PET.mgz')
        if os.path.exists(mask_image):
            convert_to_freesurfer_format(mask_image, 'mask.mgz')

        # 进行 T1 图像的标准化
        subprocess.run(['recon-all', '-s', subject_id, '-i', 'T1.mgz', '-all'])

        # 获取 MNI 空间的 T1 图像
        subprocess.run(['mri_convert', os.path.join(output_dir, 'mri/T1.mgz'), 'T1_MNI.mgz'])

        # 配准 FLAIR 和 PET 到 MNI 空间的 T1 图像
        subprocess.run(['bbregister', '--s', subject_id, '--mov', 'FLAIR.mgz', '--reg', 'FLAIR_to_MNI.dat', '--o', 'FLAIR_to_MNI.mgz', '--init-fsl'])
        #subprocess.run(['bbregister', '--s', subject_id, '--mov', 'PET.mgz', '--reg', 'PET_to_MNI.dat', '--o', 'PET_to_MNI.mgz', '--init-fsl'])

        # 配准病灶掩膜到 MNI 空间
        if os.path.exists(mask_image):
            subprocess.run(['bbregister', '--s', subject_id, '--mov', 'mask.mgz', '--reg', 'mask_to_MNI.dat', '--o', 'mask_to_MNI.mgz', '--init-fsl'])

        # 创建脑部掩膜（可选）
        subprocess.run(['mri_binarize', '--i', 'T1_MNI.mgz', '--o', 'brain_mask.mgz', '--min', '0.5'])

        # 应用脑部掩膜
        subprocess.run(['mri_mask', 'FLAIR_to_MNI.mgz', 'brain_mask.mgz', 'FLAIR_brain.mgz'])
        #subprocess.run(['mri_mask', 'PET_to_MNI.mgz', 'brain_mask.mgz', 'PET_brain.mgz'])
        if os.path.exists(mask_image):
            subprocess.run(['mri_mask', 'mask_to_MNI.mgz', 'brain_mask.mgz', 'mask_brain.mgz'])

        # 输出为 NIfTI 格式
        subprocess.run(['mri_convert', 'FLAIR_brain.mgz', 'FLAIR_brain.nii'])
        #subprocess.run(['mri_convert', 'PET_brain.mgz', 'PET_brain.nii'])
        if os.path.exists(mask_image):
            subprocess.run(['mri_convert', 'mask_brain.mgz', 'mask_brain.nii'])

        print(f"FCD preprocessing completed for {data_dir}.")

    except Exception as e:
        # 将出错的 data_dir 写入日志文件
        with open(error_log_path, 'a') as error_log:
            error_log.write(f"Error processing {data_dir}: {e}\n")
        print(f"Error processing {data_dir}. Details written to {error_log_path}.")
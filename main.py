import subprocess
import os

###
### copy file
###
# ������·��
main_path = '/home/liyin/DATA_LL/ds004199-download/'  # �滻Ϊ���·��
sapath = '/home/liyin/DATA_LL/FCD_MNI/FCD_2/'

# ������·���µ��������ļ���
for folder in os.listdir(main_path):
    
    print(folder)
    
    if 'sub' not in folder:
        continue
    
    # �������ļ��в����ڣ��򴴽���
    os.makedirs(os.path.join(sapath, folder), exist_ok=True)
    
    files = os.listdir(os.path.join(main_path, folder, 'anat'))
    
    for file in files:
        if file.endswith('T1w.nii.gz'):
            # ��ȡ NIfTI �ļ�
            file_path = os.path.join(main_path, folder, 'anat', file)
            img = nib.load(file_path)

            # ��ȡ�ռ�ֱ���
            hdr = img.header
            spacing = hdr.get_zooms()  # ��ȡÿ��ά�ȵķֱ���

            #print(f'File: {file_path}')
            print(f'Spatial Resolution: {spacing}')

            shutil.copy2(file_path, sapath+'/T1.nii.gz')

        if file.endswith('FLAIR.nii.gz'):
            # ��ȡ NIfTI �ļ�
            file_path = os.path.join(main_path, folder, 'anat', file)
            img = nib.load(file_path)

            # ��ȡ�ռ�ֱ���
            hdr = img.header
            spacing = hdr.get_zooms()  # ��ȡÿ��ά�ȵķֱ���

            #print(f'File: {file_path}')
            print(f'Spatial Resolution: {spacing}')

            shutil.copy2(file_path, sapath+'/FLAIR.nii.gz')

        if file.endswith('FLAIR_roi.nii.gz'):
            # ��ȡ NIfTI �ļ�
            file_path = os.path.join(main_path, folder, 'anat', file)
            img = nib.load(file_path)

            # ��ȡ�ռ�ֱ���
            hdr = img.header
            spacing = hdr.get_zooms()  # ��ȡÿ��ά�ȵķֱ���

            #print(f'File: {file_path}')
            print(f'Spatial Resolution: {spacing}')

            shutil.copy2(file_path, sapath+'/mask.nii.gz')
        


# ��ȡ�ļ����б�ȥ�����ļ���Ԫ�أ�����������·��
data_dir_path = '/home/liyin/DATA_LL/FCD_MNI/FCD_2/'
data_dirs = [os.path.join(data_dir_path, d) for d in os.listdir(data_dir_path) if os.path.isdir(os.path.join(data_dir_path, d))]

print(data_dirs)  # ��ӡ�ļ����б�

# ���������־�ļ�
error_log_path = 'error_log.txt'

for index,data_dir in enumerate(data_dirs):
    print(index,len(data_dirs),data_dir)
    try:
        # ���������ļ�·��
        t1_image = os.path.join(data_dir, 'T1.nii')
        flair_image = os.path.join(data_dir, 'FLAIR.nii')
        #pet_image = os.path.join(data_dir, 'PET.nii')
        #mask_image = os.path.join(data_dir, 'mask.nii')

        # ��������ļ�·��
        subject_id = os.path.basename(data_dir)  # ʹ���ļ�������Ϊ subject_id
        subjects_dir = os.environ['SUBJECTS_DIR']
        output_dir = os.path.join(subjects_dir, subject_id)

        # ȷ������ļ��д���
        os.makedirs(output_dir, exist_ok=True)

        # ׼�����ݣ�ת��Ϊ FreeSurfer ��ʽ
        convert_to_freesurfer_format(t1_image, 'T1.mgz')
        convert_to_freesurfer_format(flair_image, 'FLAIR.mgz')
        #convert_to_freesurfer_format(pet_image, 'PET.mgz')
        if os.path.exists(mask_image):
            convert_to_freesurfer_format(mask_image, 'mask.mgz')

        # ���� T1 ͼ��ı�׼��
        subprocess.run(['recon-all', '-s', subject_id, '-i', 'T1.mgz', '-all'])

        # ��ȡ MNI �ռ�� T1 ͼ��
        subprocess.run(['mri_convert', os.path.join(output_dir, 'mri/T1.mgz'), 'T1_MNI.mgz'])

        # ��׼ FLAIR �� PET �� MNI �ռ�� T1 ͼ��
        subprocess.run(['bbregister', '--s', subject_id, '--mov', 'FLAIR.mgz', '--reg', 'FLAIR_to_MNI.dat', '--o', 'FLAIR_to_MNI.mgz', '--init-fsl'])
        #subprocess.run(['bbregister', '--s', subject_id, '--mov', 'PET.mgz', '--reg', 'PET_to_MNI.dat', '--o', 'PET_to_MNI.mgz', '--init-fsl'])

        # ��׼������Ĥ�� MNI �ռ�
        if os.path.exists(mask_image):
            subprocess.run(['bbregister', '--s', subject_id, '--mov', 'mask.mgz', '--reg', 'mask_to_MNI.dat', '--o', 'mask_to_MNI.mgz', '--init-fsl'])

        # �����Բ���Ĥ����ѡ��
        subprocess.run(['mri_binarize', '--i', 'T1_MNI.mgz', '--o', 'brain_mask.mgz', '--min', '0.5'])

        # Ӧ���Բ���Ĥ
        subprocess.run(['mri_mask', 'FLAIR_to_MNI.mgz', 'brain_mask.mgz', 'FLAIR_brain.mgz'])
        #subprocess.run(['mri_mask', 'PET_to_MNI.mgz', 'brain_mask.mgz', 'PET_brain.mgz'])
        if os.path.exists(mask_image):
            subprocess.run(['mri_mask', 'mask_to_MNI.mgz', 'brain_mask.mgz', 'mask_brain.mgz'])

        # ���Ϊ NIfTI ��ʽ
        subprocess.run(['mri_convert', 'FLAIR_brain.mgz', 'FLAIR_brain.nii'])
        #subprocess.run(['mri_convert', 'PET_brain.mgz', 'PET_brain.nii'])
        if os.path.exists(mask_image):
            subprocess.run(['mri_convert', 'mask_brain.mgz', 'mask_brain.nii'])

        print(f"FCD preprocessing completed for {data_dir}.")

    except Exception as e:
        # ������� data_dir д����־�ļ�
        with open(error_log_path, 'a') as error_log:
            error_log.write(f"Error processing {data_dir}: {e}\n")
        print(f"Error processing {data_dir}. Details written to {error_log_path}.")
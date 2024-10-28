# FCD-Preprocessing
Register T1, FLAIR, PET, and mask to MNI space using FreeSurfer, and extract brain regions.

如果有一个基于 T1 图像标注的病灶掩膜 (MASK)，以及Flair、PET，可以将这个掩膜与其他图像配准并应用，以仅提取脑部病灶区域。以下是整个流程：

### 1. 准备数据

确保你的 T1、FLAIR、PET 图像以及病灶掩膜都是 NIfTI 格式（.nii 或 .nii.gz）。

### 2. 转换为 FreeSurfer 格式

将所有图像转换为 FreeSurfer 格式：
```
mri_convert T1.nii T1.mgz
mri_convert FLAIR.nii FLAIR.mgz
mri_convert PET.nii PET.mgz
mri_convert mask.nii mask.mgz  # 转换病灶掩膜
```
### 3. 进行 T1 图像的标准化
使用 recon-all 对 T1 图像进行标准化，生成 MNI 空间的脑部结构：
```
recon-all -s <subject_id> -i T1.mgz -all
```
### 4. 获取 MNI 空间的 T1 图像
完成 recon-all 后，获取 MNI 空间中的 T1 图像：
```
mri_convert $SUBJECTS_DIR/<subject_id>/mri/T1.mgz T1_MNI.mgz
```
### 5. 配准 FLAIR 和 PET 到 MNI 空间的 T1 图像
使用 bbregister 将 FLAIR 和 PET 图像配准到 MNI 空间的 T1 图像：
```
FLAIR 配准
bbregister --s <subject_id> --mov FLAIR.mgz --reg FLAIR_to_MNI.dat --o FLAIR_to_MNI.mgz --init-fsl
# PET 配准
bbregister --s <subject_id> --mov PET.mgz --reg PET_to_MNI.dat --o PET_to_MNI.mgz --init-fsl
```
### 6. 配准病灶掩膜到 MNI 空间
将病灶掩膜配准到 MNI 空间的 T1 图像：
```
bbregister --s <subject_id> --mov mask.mgz --reg mask_to_MNI.dat --o mask_to_MNI.mgz --init-fsl
```
### 7. 创建脑部掩膜（可选）
如果你需要进一步提取脑部区域，可以创建一个脑部掩膜：
```
mri_binarize --i T1_MNI.mgz --o brain_mask.mgz --min 0.5
```
### 8. 应用脑部掩膜
如果你创建了脑部掩膜，将其应用于 FLAIR、PET 和病灶掩膜，以仅保留脑部区域：
```
mri_mask FLAIR_to_MNI.mgz brain_mask.mgz FLAIR_brain.mgz
mri_mask PET_to_MNI.mgz brain_mask.mgz PET_brain.mgz
mri_mask mask_to_MNI.mgz brain_mask.mgz mask_brain.mgz  # 应用到病灶掩膜
```
### 9. 输出为 NIfTI 格式
将最终的脑部图像和掩膜转换为 NIfTI 格式：
```
mri_convert FLAIR_brain.mgz FLAIR_brain.nii
mri_convert PET_brain.mgz PET_brain.nii
mri_convert mask_brain.mgz mask_brain.nii
```
### 10. 可视化检查
使用 FreeSurfer 的 freeview 查看最终结果：
```
freeview T1_MNI.mgz FLAIR_brain.mgz PET_brain.mgz mask_brain.mgz
```

### 这样，你就可以将病灶掩膜与其他图像配准并提取脑部区域。

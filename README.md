# DCT tool for MediaTek devices

If you want to use this tools, simply use

    python2 DrvGen.py example.dws out out

inside this folder. It is highly recommended to move the generated cust.dtsi to
your device kernel at arch/arm64/boot/dts/include/example for allow the generation of dtbo files.

## Supported platforms
Currently, only those platforms are supported by the DCT tool

- MT6739
- MT6761
- MT6765
- MT6768
- MT6771
- MT6785
- MT6853
- MT6873
- MT6885

## Repository Details
This repository uses DCT from [android_kernel_oneplus_mt6893](https://github.com/OnePlusOSS/android_kernel_oneplus_mt6893/) as base till `dc833d7958fa0a2ec761193b50dde494b3f289eb`.
After that, MediaTek moved the DCT tool inside the BSP.

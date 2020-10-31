# DCT tool for MediaTek devices

If you want to use this tools, simply use

    python3 DrvGen.py example.dws out out

inside this folder. It is highly recommended to move the generated cust.dtsi to
your device kernel at arch/arm64/boot/dts/include/example for allow the generation of dtbo files.

## Supported platforms
Currently, only those platforms are fully supported by the DCT tool

- MT6739
- MT6761
- MT6765
- MT6768
- MT6771
- MT6779
- MT6785
- MT6833
- MT6853
- MT6873
- MT6880
- MT6885
- MT6893

## Repository Details
This repository uses DCT from MediaTek BSP (ALPS R MP1 V8.46).

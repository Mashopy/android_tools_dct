#! /usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright Statement:
#
# This software/firmware and related documentation ("MediaTek Software") are
# protected under relevant copyright laws. The information contained herein is
# confidential and proprietary to MediaTek Inc. and/or its licensors. Without
# the prior written permission of MediaTek inc. and/or its licensors, any
# reproduction, modification, use or disclosure of MediaTek Software, and
# information contained herein, in whole or in part, shall be strictly
# prohibited.
#
# MediaTek Inc. (C) 2019. All rights reserved.
#
# BY OPENING THIS FILE, RECEIVER HEREBY UNEQUIVOCALLY ACKNOWLEDGES AND AGREES
# THAT THE SOFTWARE/FIRMWARE AND ITS DOCUMENTATIONS ("MEDIATEK SOFTWARE")
# RECEIVED FROM MEDIATEK AND/OR ITS REPRESENTATIVES ARE PROVIDED TO RECEIVER
# ON AN "AS-IS" BASIS ONLY. MEDIATEK EXPRESSLY DISCLAIMS ANY AND ALL
# WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE OR
# NONINFRINGEMENT. NEITHER DOES MEDIATEK PROVIDE ANY WARRANTY WHATSOEVER WITH
# RESPECT TO THE SOFTWARE OF ANY THIRD PARTY WHICH MAY BE USED BY,
# INCORPORATED IN, OR SUPPLIED WITH THE MEDIATEK SOFTWARE, AND RECEIVER AGREES
# TO LOOK ONLY TO SUCH THIRD PARTY FOR ANY WARRANTY CLAIM RELATING THERETO.
# RECEIVER EXPRESSLY ACKNOWLEDGES THAT IT IS RECEIVER'S SOLE RESPONSIBILITY TO
# OBTAIN FROM ANY THIRD PARTY ALL PROPER LICENSES CONTAINED IN MEDIATEK
# SOFTWARE. MEDIATEK SHALL ALSO NOT BE RESPONSIBLE FOR ANY MEDIATEK SOFTWARE
# RELEASES MADE TO RECEIVER'S SPECIFICATION OR TO CONFORM TO A PARTICULAR
# STANDARD OR OPEN FORUM. RECEIVER'S SOLE AND EXCLUSIVE REMEDY AND MEDIATEK'S
# ENTIRE AND CUMULATIVE LIABILITY WITH RESPECT TO THE MEDIATEK SOFTWARE
# RELEASED HEREUNDER WILL BE, AT MEDIATEK'S OPTION, TO REVISE OR REPLACE THE
# MEDIATEK SOFTWARE AT ISSUE, OR REFUND ANY SOFTWARE LICENSE FEES OR SERVICE
# CHARGE PAID BY RECEIVER TO MEDIATEK FOR SUCH MEDIATEK SOFTWARE AT ISSUE.
#
# The following software/firmware and/or related documentation ("MediaTek
# Software") have been modified by MediaTek Inc. All revisions are subject to
# any receiver's applicable license agreements with MediaTek Inc.

import os, sys
import collections
import xml.dom.minidom

from obj.GpioObj import GpioObj
from obj.GpioObj import GpioObj_MT6799
from obj.GpioObj import GpioObj_MT6759
from obj.GpioObj import GpioObj_MT6739
from obj.GpioObj import GpioObj_MT6771
from obj.GpioObj import GpioObj_MT6763
from obj.GpioObj import GpioObj_MT6768
from obj.GpioObj import GpioObj_MT6785

from obj.EintObj import EintObj
from obj.EintObj import EintObj_MT6750S
from obj.EintObj import EintObj_MT6739
from obj.EintObj import EintObj_MT6885
from obj.EintObj import EintObj_MT6853

from obj.AdcObj import AdcObj
from obj.AdcObj import AdcObj_MT6785

from obj.ClkObj import ClkObj
from obj.ClkObj import ClkObj_MT6797
from obj.ClkObj import ClkObj_MT6757
from obj.ClkObj import ClkObj_MT6570
from obj.ClkObj import ClkObj_MT6779

from obj.I2cObj import I2cObj
from obj.I2cObj import I2cObj_MT6759
from obj.I2cObj import I2cObj_MT6775

from obj.PmicObj import PmicObj
from obj.PmicObj import PmicObj_MT6758

from obj.Md1EintObj import Md1EintObj
from obj.Md1EintObj import Md1EintObj_MT6739
from obj.PowerObj import PowerObj
from obj.KpdObj import KpdObj
from obj.RfioObj import RfioObj
from obj.ModuleObj import ModuleObj

from utility.util import log
from utility.util import LogLevel

para_map = {'adc':['adc_h', 'adc_dtsi'],\
            'clk':['clk_buf_h', 'clk_buf_dtsi'],\
            'i2c':['i2c_h', 'i2c_dtsi'],\
            'eint':['eint_h', 'eint_dtsi'],\
            'gpio':['gpio_usage_h', 'gpio_boot_h', 'gpio_dtsi', 'scp_gpio_usage_h', 'pinfunc_h', \
                    'pinctrl_h', 'gpio_usage_mapping_dtsi'],\
            'md1_eint':['md1_eint_h', 'md1_eint_dtsi'],\
            'kpd':['kpd_h', 'kpd_dtsi'],\
            'pmic':['pmic_drv_h', 'pmic_drv_c', 'pmic_h', 'pmic_c', 'pmic_dtsi'],\
            'power':['power_h'],\
            'rfio':['digrf_io_cfgtable.c']}

class ChipObj:
    def __init__(self, path, dest):
        self.__epFlag = False
        self.__path = path
        ModuleObj.set_genPath(dest)
        self.__objs = collections.OrderedDict()

        self.init_objs()

    def init_objs(self):
        self.__objs['adc'] = AdcObj()
        self.__objs['clk'] = ClkObj()
        self.__objs["i2c"] = I2cObj()
        self.__objs["gpio"] = GpioObj()
        # eint obj need gpio data
        self.__objs["eint"] = EintObj(self.__objs['gpio'])
        self.__objs["md1_eint"] = Md1EintObj()

        self.__objs["pmic"] = PmicObj()
        self.__objs["power"] = PowerObj()
        self.__objs["kpd"] = KpdObj()

        path = os.path.join(sys.path[0], 'config', 'RFIO.cmp')
        if os.path.exists(path):
            self.__objs['rfio'] = RfioObj()

    def replace_obj(self, tag, obj):
        if not tag in self.__objs.keys():
            return False

        self.__objs[tag] = obj

    def get_gpioObj(self):
        return self.__objs['gpio']

    def refresh_eintGpioMap(self):
        self.__objs['eint'].set_gpioObj(self.__objs['gpio'])

    def append_obj(self, tag, obj):
        if tag in self.__objs.keys():
            return False

        self.__objs[tag] = obj

    @staticmethod
    def get_chipId(path):
        if not os.path.exists(path):
            msg = '%s is not a available path!' %(path)
            log(LogLevel.error, msg)
            return False
        data = xml.dom.minidom.parse(path)
        root = data.documentElement
        # get 'general' node
        node = root.getElementsByTagName('general')
        return node[0].getAttribute('chip')

    def parse(self):
        if not os.path.exists(self.__path):
            msg = '%s is not a available path!' %(self.__path)
            log(LogLevel.error, msg)
            return False

        data = xml.dom.minidom.parse(self.__path)

        root = data.documentElement
        # get 'general' node
        node = root.getElementsByTagName('general')
        # get chip name and project name
        ModuleObj.set_chipId(node[0].getAttribute('chip'))

        # get early porting flag
        epNode = node[0].getElementsByTagName('ep')
        if len(epNode) != 0 and epNode[0].childNodes[0].nodeValue=="True":
            self.__epFlag = True

        msg = 'Chip ID : %s' %(node[0].getAttribute('chip'))
        log(LogLevel.info, msg)
        msg = 'Project Info: %s' %(node[0].getElementsByTagName('proj')[0].childNodes[0].nodeValue)
        log(LogLevel.info, msg)

        # initialize the objects mapping table
        self.init_objs()
        # get module nodes from .DWS file
        nodes = node[0].getElementsByTagName('module')

        for node in nodes:
            tag = node.getAttribute('name')
            obj = self.create_obj(tag)
            if obj == None:
                msg = 'can not find %s node in DWS!' %(tag)
                log(LogLevel.error, msg)
                return False
            obj.parse(node)

        return True

    def generate(self, paras):
        if len(paras) == 0:
            for obj in self.__objs.values():
                obj.gen_files()

            self.gen_custDtsi()
        else:
            self.gen_spec(paras)

        return True

    def create_obj(self, tag):
        obj = None
        if tag in self.__objs.keys():
            obj = self.__objs[tag]

        return obj


    def gen_spec(self, paras):
        # if cmp(paras[0], 'cust_dtsi') == 0:
            # self.gen_custDtsi()
            # return True

        for para in paras:
            if para == 'cust_dtsi':
                self.gen_custDtsi()
                continue

            idx = 0
            name = ''
            if para.strip() != '':
                for value in para_map.values():
                    if para in value:
                        name = para_map.keys()[idx]
                        break
                    idx += 1

            if name != '':
                log(LogLevel.info, 'Start to generate %s file...' %(para))
                obj = self.__objs[name]
                obj.gen_spec(para)
                log(LogLevel.info, 'Generate %s file successfully!' %(para))
            else:
                log(LogLevel.warn, '%s can not be recognized!' %(para))
                # sys.exit(-1)

        return True

    def gen_custDtsi(self):
        log(LogLevel.info, 'Start to generate cust_dtsi file...')
        fp = open(os.path.join(ModuleObj.get_genPath(), 'cust.dtsi'), 'w')
        gen_str = ModuleObj.writeComment()

        # if early porting, gen empty dtsi file for kernel
        if self.__epFlag:
            fp.write(gen_str)
            fp.close()
            return

        #sorted_list = sorted(self.__objs.keys())
        #for tag in sorted_list:
        for tag in self.__objs.keys():
            if tag == 'gpio':
                gpioObj = self.create_obj(tag)
                gen_str += ModuleObj.writeHeader(gpioObj.get_dtsiFileName())
                gen_str += gpioObj.fill_mapping_dtsiFile()
                gen_str += gpioObj.fill_init_default_dtsiFile()
            else:
                obj = self.create_obj(tag)
                gen_str += ModuleObj.writeHeader(obj.get_dtsiFileName())
                gen_str += obj.fill_dtsiFile()

            gen_str += '''\n\n'''

        fp.write(gen_str)
        fp.close()
        log(LogLevel.info, 'Generate cust_dtsi file successfully!')


class MT6797(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)
        self.init_objs()

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'clk', ClkObj_MT6797())

    def parse(self):
        return ChipObj.parse(self)

    def generate(self, paras):
        return ChipObj.generate(self, paras)


class MT6757(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'clk', ClkObj_MT6757())
        ChipObj.replace_obj(self, 'i2c', I2cObj_MT6759())

    def parse(self):
        return ChipObj.parse(self)


    def generate(self, paras):
        return ChipObj.generate(self, paras)


class MT6757_P25(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'clk', ClkObj_Olympus())
        ChipObj.replace_obj(self, 'i2c', I2cObj_MT6759())

    def parse(self):
        return ChipObj.parse(self)

    def generate(self, paras):
        return ChipObj.generate(self, paras)


class MT6570(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'clk', ClkObj_MT6570())

    def parse(self):
        return ChipObj.parse(self)


    def generate(self, paras):
        return ChipObj.generate(self, paras)

class MT6799(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'gpio', GpioObj_MT6799())
        ChipObj.replace_obj(self, 'i2c', I2cObj_MT6759())
        ChipObj.refresh_eintGpioMap(self)

    def parse(self):
        log(LogLevel.info, 'MT6799 parse')
        return ChipObj.parse(self)

    def generate(self, paras):
        return ChipObj.generate(self, paras)

class MT6759(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'gpio', GpioObj_MT6759())
        ChipObj.replace_obj(self, 'i2c', I2cObj_MT6759())
        ChipObj.refresh_eintGpioMap(self)

    def parse(self):
        return ChipObj.parse(self)

    def generate(self, paras):
        return ChipObj.generate(self, paras)

class MT6758(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'pmic', PmicObj_MT6758())
        ChipObj.replace_obj(self, 'gpio', GpioObj_MT6739())
        ChipObj.replace_obj(self, 'eint', EintObj_MT6739(ChipObj.get_gpioObj(self)))
        ChipObj.replace_obj(self, 'i2c', I2cObj_MT6759())
        ChipObj.replace_obj(self, 'md1_eint', Md1EintObj_MT6739())
        ChipObj.refresh_eintGpioMap(self)

    def parse(self):
        return ChipObj.parse(self)

    def generate(self, paras):
        return ChipObj.generate(self, paras)

class MT6763(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'gpio', GpioObj_MT6763())
        ChipObj.replace_obj(self, 'i2c', I2cObj_MT6759())
        ChipObj.refresh_eintGpioMap(self)

    def parse(self):
        return ChipObj.parse(self)

    def generate(self, paras):
        return ChipObj.generate(self, paras)

class MT6739(MT6763):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'pmic', PmicObj_MT6758())
        ChipObj.replace_obj(self, 'gpio', GpioObj_MT6739())
        ChipObj.replace_obj(self, 'eint', EintObj_MT6739(ChipObj.get_gpioObj(self)))
        ChipObj.replace_obj(self, 'md1_eint', Md1EintObj_MT6739())
        ChipObj.replace_obj(self, 'i2c', I2cObj_MT6759())
        ChipObj.refresh_eintGpioMap(self)

    def parse(self):
        return ChipObj.parse(self)

    def generate(self, paras):
        return ChipObj.generate(self, paras)

class MT6750S(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'clk', ClkObj_MT6757())
        ChipObj.replace_obj(self, 'eint', EintObj_MT6750S(ChipObj.get_gpioObj(self)))
        ChipObj.refresh_eintGpioMap(self)

    def parse(self):
        return ChipObj.parse(self)

    def generate(self, paras):
        return ChipObj.generate(self, paras)

class MT8695(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'gpio', GpioObj_MT6799())
        ChipObj.refresh_eintGpioMap(self)

    def parse(self):
        return ChipObj.parse(self)

    def generate(self, paras):
        return ChipObj.generate(self, paras)

class MT6771(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'adc', AdcObj_MT6785())
        ChipObj.replace_obj(self, 'pmic', PmicObj_MT6758())
        ChipObj.replace_obj(self, 'gpio', GpioObj_MT6771())
        ChipObj.replace_obj(self, 'eint', EintObj_MT6739(ChipObj.get_gpioObj(self)))
        ChipObj.replace_obj(self, 'md1_eint', Md1EintObj_MT6739())
        ChipObj.replace_obj(self, 'i2c', I2cObj_MT6775())
        ChipObj.refresh_eintGpioMap(self)

class MT6775(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'pmic', PmicObj_MT6758())
        ChipObj.replace_obj(self, 'gpio', GpioObj_MT6739())
        ChipObj.replace_obj(self, 'eint', EintObj_MT6739(ChipObj.get_gpioObj(self)))
        ChipObj.replace_obj(self, 'md1_eint', Md1EintObj_MT6739())
        ChipObj.replace_obj(self, 'i2c', I2cObj_MT6775())
        ChipObj.refresh_eintGpioMap(self)


class MT6779(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'clk', ClkObj_MT6779())
        ChipObj.replace_obj(self, 'pmic', PmicObj_MT6758())
        ChipObj.replace_obj(self, 'gpio', GpioObj_MT6771())
        ChipObj.replace_obj(self, 'eint', EintObj_MT6739(ChipObj.get_gpioObj(self)))
        ChipObj.replace_obj(self, 'md1_eint', Md1EintObj_MT6739())
        ChipObj.replace_obj(self, "i2c", I2cObj_MT6775())
        ChipObj.refresh_eintGpioMap(self)

class MT6785(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'adc', AdcObj_MT6785())
        ChipObj.replace_obj(self, 'clk', ClkObj_MT6779())
        ChipObj.replace_obj(self, 'pmic', PmicObj_MT6758())
        ChipObj.replace_obj(self, 'gpio', GpioObj_MT6785())
        ChipObj.replace_obj(self, 'eint', EintObj_MT6739(ChipObj.get_gpioObj(self)))
        ChipObj.replace_obj(self, 'md1_eint', Md1EintObj_MT6739())
        ChipObj.replace_obj(self, "i2c", I2cObj_MT6775())
        ChipObj.refresh_eintGpioMap(self)

class MT6885(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'adc', AdcObj_MT6785())
        ChipObj.replace_obj(self, 'clk', ClkObj_MT6779())
        ChipObj.replace_obj(self, 'pmic', PmicObj_MT6758())
        ChipObj.replace_obj(self, 'gpio', GpioObj_MT6785())
        ChipObj.replace_obj(self, 'eint', EintObj_MT6885(ChipObj.get_gpioObj(self)))
        ChipObj.replace_obj(self, 'md1_eint', Md1EintObj_MT6739())
        ChipObj.replace_obj(self, "i2c", I2cObj_MT6775())
        ChipObj.refresh_eintGpioMap(self)

class MT6853(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'adc', AdcObj_MT6785())
        ChipObj.replace_obj(self, 'clk', ClkObj_MT6779())
        ChipObj.replace_obj(self, 'pmic', PmicObj_MT6758())
        ChipObj.replace_obj(self, 'gpio', GpioObj_MT6785())
        ChipObj.replace_obj(self, 'eint', EintObj_MT6853(ChipObj.get_gpioObj(self)))
        ChipObj.replace_obj(self, 'md1_eint', Md1EintObj_MT6739())
        ChipObj.replace_obj(self, "i2c", I2cObj_MT6775())
        ChipObj.refresh_eintGpioMap(self)

class MT6768(ChipObj):
    def __init__(self, dws_path, gen_path):
        ChipObj.__init__(self, dws_path, gen_path)

    def init_objs(self):
        ChipObj.init_objs(self)
        ChipObj.replace_obj(self, 'adc', AdcObj_MT6785())
        ChipObj.replace_obj(self, 'pmic', PmicObj_MT6758())
        ChipObj.replace_obj(self, 'gpio', GpioObj_MT6768())
        ChipObj.replace_obj(self, 'eint', EintObj_MT6739(ChipObj.get_gpioObj(self)))
        ChipObj.replace_obj(self, 'md1_eint', Md1EintObj_MT6739())
        ChipObj.replace_obj(self, "i2c", I2cObj_MT6775())
        ChipObj.refresh_eintGpioMap(self)

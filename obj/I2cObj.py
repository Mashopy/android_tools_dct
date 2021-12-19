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

import re
import string
import xml.dom.minidom
import configparser

from obj.ModuleObj import ModuleObj
#from utility import util
from utility.util import sorted_key
from data.I2cData import I2cData
from data.I2cData import BusData
import obj.ChipObj

class I2cObj(ModuleObj):
    _busList = []
    _bBusEnable = True
    def __init__(self):
        ModuleObj.__init__(self, 'cust_i2c.h', 'cust_i2c.dtsi')
        #self.__busList = []
        #self.__bBusEnable = True

    def get_cfgInfo(self):
        cp = configparser.ConfigParser(allow_no_value=True, strict=False)
        cp.read(ModuleObj.get_figPath())

        I2cData._i2c_count = int(cp.get('I2C', 'I2C_COUNT'))
        I2cData._channel_count = int(cp.get('I2C', 'CHANNEL_COUNT'))

        if cp.has_option('Chip Type', 'I2C_BUS'):
            flag = cp.get('Chip Type', 'I2C_BUS')
            if flag == '0':
                self._bBusEnable = False

        if cp.has_option('Chip Type', 'I2C_BUS'):
            flag = cp.get('Chip Type', 'I2C_BUS')
            if flag == '0':
                self._bBusEnable = False

    def read(self, node):
        nodes = node.childNodes
        for node in nodes:
            if node.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
                if node.nodeName == 'count':
                    self.__count = node.childNodes[0].nodeValue
                    continue
                if node.nodeName.find('bus') != -1:
                    speedNode = node.getElementsByTagName('speed_kbps')
                    enableNode = node.getElementsByTagName('pullPushEn')

                    data = BusData()
                    if len(speedNode):
                        data.set_speed(speedNode[0].childNodes[0].nodeValue)
                    if len(enableNode):
                        data.set_enable(enableNode[0].childNodes[0].nodeValue)

                    self._busList.append(data)
                    #I2cData._busList.append(data)
                elif node.nodeName.find('device') != -1:
                    nameNode = node.getElementsByTagName('varName')
                    channelNode = node.getElementsByTagName('channel')
                    addrNode = node.getElementsByTagName('address')

                    data = I2cData()
                    if len(nameNode):
                        data.set_varName(nameNode[0].childNodes[0].nodeValue)
                    if len(channelNode):
                        data.set_channel(channelNode[0].childNodes[0].nodeValue)
                    if len(addrNode):
                        data.set_address(addrNode[0].childNodes[0].nodeValue)

                    ModuleObj.set_data(self, node.nodeName, data)

        return True

    def parse(self, node):
        self.get_cfgInfo()
        self.read(node)

    def gen_files(self):
        ModuleObj.gen_files(self)

    def gen_spec(self, para):
        ModuleObj.gen_spec(self, para)

    def fill_hFile(self):
        gen_str = ''
        for i in range(0, I2cData._channel_count):
            gen_str += '''#define I2C_CHANNEL_%d\t\t\t%d\n''' %(i, i)

        gen_str += '''\n'''

        #sorted_lst = sorted(ModuleObj.get_data(self).keys(), key=compare)
        for key in sorted_key(ModuleObj.get_data(self).keys()):
            value = ModuleObj.get_data(self)[key]
            temp = ''
            if value.get_address().strip() == '':
                temp = 'TRUE'
            else:
                temp = 'FALSE'
            gen_str += '''#define I2C_%s_AUTO_DETECT\t\t\t%s\n''' %(value.get_varName(), temp)
            gen_str += '''#define I2C_%s_CHANNEL\t\t\t%s\n''' %(value.get_varName(), value.get_channel())
            gen_str += '''#define I2C_%s_SLAVE_7_BIT_ADDR\t\t%s\n''' %(value.get_varName(), value.get_address().upper())
            gen_str += '''\n'''

        return gen_str

    def fill_dtsiFile(self):
        gen_str = ''
        for i in range(0, I2cData._channel_count):
            if i >= len(self._busList):
                break
            gen_str += '''&i2c%d {\n''' %(i)
            gen_str += '''\t#address-cells = <1>;\n'''
            gen_str += '''\t#size-cells = <0>;\n'''


            if self._bBusEnable:
                gen_str += '''\tclock-frequency = <%d>;\n''' %(int(self._busList[i].get_speed()) * 1000)
                temp_str = ''

                if self._busList[i].get_enable() == 'false':
                    temp_str = 'use-open-drain'
                elif self._busList[i].get_enable() == 'true':
                    temp_str = 'use-push-pull'
                gen_str += '''\tmediatek,%s;\n''' %(temp_str)

            for key in sorted_key(ModuleObj.get_data(self).keys()):
                value = ModuleObj.get_data(self)[key]
                channel = 'I2C_CHANNEL_%d' %(i)
                if value.get_channel() == channel and value.get_varName() != 'NC' and value.get_address().strip() != '':
                    gen_str += '''\t%s@%s {\n''' %(value.get_varName().lower(), value.get_address()[2:].lower())
                    gen_str += '''\t\tcompatible = \"mediatek,%s\";\n''' %(value.get_varName().lower())
                    gen_str += '''\t\treg = <%s>;\n''' %(value.get_address().lower())
                    gen_str += '''\t\tstatus = \"okay\";\n'''
                    gen_str += '''\t};\n\n'''

            gen_str += '''};\n\n'''

        return gen_str

class I2cObj_MT6759(I2cObj):
    def __init__(self):
        I2cObj.__init__(self)

    def parse(self, node):
        I2cObj.parse(self, node)

    def gen_files(self):
        I2cObj.gen_files(self)

    def gen_spec(self, para):
        I2cObj.gen_spec(self, para)

    def fill_dtsiFile(self):
        gen_str = ''
        for i in range(0, I2cData._channel_count):
            if i >= len(self._busList):
                break
            gen_str += '''&i2c%d {\n''' %(i)
            gen_str += '''\t#address-cells = <1>;\n'''
            gen_str += '''\t#size-cells = <0>;\n'''


            if self._bBusEnable:
                gen_str += '''\tclock-frequency = <%d>;\n''' %(int(self._busList[i].get_speed()) * 1000)
                temp_str = ''

                if self._busList[i].get_enable() == 'false':
                    temp_str = 'use-open-drain'
                elif self._busList[i].get_enable() == 'true':
                    temp_str = 'use-push-pull'
                gen_str += '''\tmediatek,%s;\n''' %(temp_str)

            for key in sorted_key(ModuleObj.get_data(self).keys()):
                value = ModuleObj.get_data(self)[key]
                channel = 'I2C_CHANNEL_%d' %(i)
                if value.get_channel() == channel and value.get_varName() != 'NC' and value.get_address().strip() != '':
                    gen_str += '''\t%s_mtk:%s@%s {\n''' %(value.get_varName().lower(), value.get_varName().lower(), value.get_address()[2:].lower())
                    gen_str += '''\t\tcompatible = \"mediatek,%s\";\n''' %(value.get_varName().lower())
                    gen_str += '''\t\treg = <%s>;\n''' %(value.get_address().lower())
                    gen_str += '''\t\tstatus = \"okay\";\n'''
                    gen_str += '''\t};\n\n'''

            gen_str += '''};\n\n'''

        return gen_str

class I2cObj_MT6775(I2cObj):
    def __init__(self):
        I2cObj.__init__(self)

    def fill_dtsiFile(self):
        gen_str = ''
        for i in range(0, I2cData._channel_count):
            if i >= len(self._busList):
                break
            gen_str += '''&i2c%d {\n''' %(i)
            gen_str += '''\t#address-cells = <1>;\n'''
            gen_str += '''\t#size-cells = <0>;\n'''


            if self._bBusEnable:
                gen_str += '''\tclock-frequency = <%d>;\n''' %(int(self._busList[i].get_speed()) * 1000)
                temp_str = ''

                if self._busList[i].get_enable() == 'false':
                    temp_str = 'use-open-drain'
                elif self._busList[i].get_enable() == 'true':
                    temp_str = 'use-push-pull'
                gen_str += '''\tmediatek,%s;\n''' %(temp_str)

            for key in sorted_key(ModuleObj.get_data(self).keys()):
                value = ModuleObj.get_data(self)[key]
                channel = 'I2C_CHANNEL_%d' %(i)
                if value.get_channel() == channel and value.get_varName() != 'NC' and value.get_address().strip() != '':
                    gen_str += '''\t%s_mtk:%s@%s {\n''' %(value.get_varName().lower(), value.get_varName().lower(), value.get_address()[2:].lower())
                    if re.match(r'^RT[\d]+$', value.get_varName()):
                        gen_str += '''\t\tcompatible = \"richtek,%s\";\n''' %(value.get_varName().lower())
                    else:
                        gen_str += '''\t\tcompatible = \"mediatek,%s\";\n''' %(value.get_varName().lower())
                    gen_str += '''\t\treg = <%s>;\n''' %(value.get_address().lower())
                    gen_str += '''\t\tstatus = \"okay\";\n'''
                    gen_str += '''\t};\n\n'''

            gen_str += '''};\n\n'''

        return gen_str

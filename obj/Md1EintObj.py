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

import configparser
import string
import xml.dom.minidom
from itertools import dropwhile
import re

from utility import util
from utility.util import sorted_key
from obj.ModuleObj import ModuleObj
from data.Md1EintData import Md1EintData
from utility.util import LogLevel

class Md1EintObj(ModuleObj):
    def __init__(self):
        ModuleObj.__init__(self, 'cust_eint_md1.h', 'cust_md1_eint.dtsi')
        self.__srcPin = {}
        self.__bSrcPinEnable = True

    def get_cfgInfo(self):
        # ConfigParser accept ":" and "=", so SRC_PIN will be treated specially
        cp = configparser.ConfigParser(allow_no_value=True, strict=False)
        cp.read(ModuleObj.get_figPath())

        if cp.has_option('Chip Type', 'MD1_EINT_SRC_PIN'):
            flag = cp.get('Chip Type', 'MD1_EINT_SRC_PIN')
            if flag == '0':
                self.__bSrcPinEnable = False

        if(self.__bSrcPinEnable):
            #for option in cp.options('SRC_PIN'):
                #value = cp.get('SRC_PIN', option)
                #value = value[1:]
                #temp = value.split('=')
                #self.__srcPin[temp[0]] = temp[1]

            with open(ModuleObj.get_figPath()) as file:
                src_pin_expr = r"^.+\s*::\s*(\w+)\s*=\s*(\w+)\s*$"
                reg = re.compile(src_pin_expr)
                for line in dropwhile(lambda line: not line.lstrip().startswith("[SRC_PIN]"), file):
                    match_obj = reg.match(line)
                    if match_obj:
                        self.__srcPin[match_obj.group(1)] = match_obj.group(2)
        else:
            self.__srcPin[''] = '-1'

    def read(self, node):
        nodes = node.childNodes
        try:
            for node in nodes:
                if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                    if node.nodeName == 'count':
                        self.__count = node.childNodes[0].nodeValue
                        continue

                    varNode = node.getElementsByTagName('varName')
                    detNode = node.getElementsByTagName('debounce_time')
                    polNode = node.getElementsByTagName('polarity')
                    senNode = node.getElementsByTagName('sensitive_level')
                    deeNode = node.getElementsByTagName('debounce_en')
                    dedNode = node.getElementsByTagName('dedicated_en')
                    srcNode = node.getElementsByTagName('srcPin')
                    sktNode = node.getElementsByTagName('socketType')

                    data = Md1EintData()
                    if len(varNode):
                        data.set_varName(varNode[0].childNodes[0].nodeValue)
                    if len(detNode):
                        data.set_debounceTime(detNode[0].childNodes[0].nodeValue)
                    if len(polNode):
                        data.set_polarity(polNode[0].childNodes[0].nodeValue)
                    if len(senNode):
                        data.set_sensitiveLevel(senNode[0].childNodes[0].nodeValue)
                    if len(deeNode):
                        data.set_debounceEnable(deeNode[0].childNodes[0].nodeValue)
                    if len(dedNode):
                        data.set_dedicatedEn(dedNode[0].childNodes[0].nodeValue)
                    if len(srcNode) and len(srcNode[0].childNodes):
                        data.set_srcPin(srcNode[0].childNodes[0].nodeValue)
                    if len(sktNode) and len(sktNode[0].childNodes):
                        data.set_socketType(sktNode[0].childNodes[0].nodeValue)

                    ModuleObj.set_data(self, node.nodeName, data)
        except:
            msg = 'read md1_eint content fail!'
            util.log(LogLevel.error, msg)
            return False

        return True

    def parse(self, node):
        self.get_cfgInfo()
        self.read(node)

    def gen_files(self):
        ModuleObj.gen_files(self)

    def fill_hFile(self):
        gen_str = ''
        gen_str += '''#define CUST_EINT_MD_LEVEL_SENSITIVE\t\t0\n'''
        gen_str += '''#define CUST_EINT_MD_EDGE_SENSITIVE\t\t1\n'''

        gen_str += '''\n'''

        if self.__bSrcPinEnable:
            for (key, value) in self.__srcPin.items():
                gen_str += '''#define %s\t\t%s\n''' %(key, value)
            gen_str += '''\n'''

        gen_str += '''#define CUST_EINT_POLARITY_LOW\t\t0\n'''
        gen_str += '''#define CUST_EINT_POLARITY_HIGH\t\t1\n'''
        gen_str += '''\n'''

        gen_str += '''#define CUST_EINT_LEVEL_SENSITIVE\t\t0\n'''
        gen_str += '''#define CUST_EINT_EDGE_SENSITIVE\t\t1\n'''
        gen_str += '''\n'''

        count = 0
        for key in sorted_key(ModuleObj.get_data(self).keys()):
            value = ModuleObj.get_data(self)[key]
            if value.get_varName() == 'NC':
                continue
            num = key[4:]
            count += 1
            gen_str += '''#define CUST_EINT_MD1_%s_NAME\t\t\t"%s"\n''' %(num, value.get_varName())
            gen_str += '''#define CUST_EINT_MD1_%s_NUM\t\t\t%s\n''' %(num, num)
            gen_str += '''#define CUST_EINT_MD1_%s_DEBOUNCE_CN\t\t%s\n''' %(num, value.get_debounceTime())
            gen_str += '''#define CUST_EINT_MD1_%s_POLARITY\t\tCUST_EINT_POLARITY_%s\n''' %(num, value.get_polarity().upper())
            gen_str += '''#define CUST_EINT_MD1_%s_SENSITIVE\t\tCUST_EINT_MD_%s_SENSITIVE\n''' %(num, value.get_sensitiveLevel().upper())
            gen_str += '''#define CUST_EINT_MD1_%s_DEBOUNCE_EN\t\tCUST_EINT_DEBOUNCE_%s\n''' %(num, value.get_debounceEnable().upper())
            gen_str += '''#define CUST_EINT_MD1_%s_DEDICATED_EN\t\t%s\n''' %(num, int(value.get_dedicatedEn()))
            if self.__bSrcPinEnable:
                gen_str += '''#define CUST_EINT_MD1_%s_SRCPIN\t\t\t%s\n''' %(num, value.get_srcPin())
            gen_str += '''\n'''

        gen_str += '''#define CUST_EINT_MD1_CNT\t\t\t%d\n''' %(count)

        return gen_str


    def fill_dtsiFile(self):
        gen_str = ''
        gen_str += '''&eintc {\n'''
        for key in sorted_key(ModuleObj.get_data(self).keys()):
            value = ModuleObj.get_data(self)[key]
            if value.get_varName() == 'NC':
                continue
            num = key[4:]
            gen_str += '''\t%s@%s {\n''' %(value.get_varName(), num)
            gen_str += '''\t\tcompatible = \"mediatek,%s-eint\";\n''' %(value.get_varName())

            type = 1
            polarity = value.get_polarity()
            sensitive = value.get_sensitiveLevel()

            if polarity == 'High' and sensitive == 'Edge':
                type = 1
            elif polarity == 'Low' and sensitive == 'Edge':
                type = 2
            elif polarity == 'High' and sensitive == 'Level':
                type = 4
            elif polarity == 'Low' and sensitive == 'Level':
                type = 8

            gen_str += '''\t\tinterrupts = <%s %d>;\n''' %(num, type)
            gen_str += '''\t\tdebounce = <%s %d>;\n''' %(num, (int(value.get_debounceTime()))*1000)
            gen_str += '''\t\tdedicated = <%s %d>;\n''' %(num, int(value.get_dedicatedEn()))
            if self.__bSrcPinEnable:
                gen_str += '''\t\tsrc_pin = <%s %s>;\n''' %(num, self.__srcPin[value.get_srcPin()])
            else:
                gen_str += '''\t\tsrc_pin = <%s %s>;\n''' %(num, -1)
            gen_str += '''\t\tsockettype = <%s %s>;\n''' %(num, value.get_socketType())
            gen_str += '''\t\tstatus = \"okay\";\n'''
            gen_str += '''\t};\n'''

            gen_str += '''\n'''

        gen_str += '''};\n'''

        return gen_str

    def get_srcPin(self):
        return self.__srcPin

    def get_srcPinEnable(self):
        return self.__bSrcPinEnable

class Md1EintObj_MT6739(Md1EintObj):
    def __init__(self):
        Md1EintObj.__init__(self)

    def fill_dtsiFile(self):
        gen_str = ''
        for key in sorted_key(ModuleObj.get_data(self).keys()):
            value = ModuleObj.get_data(self)[key]
            if value.get_varName() == 'NC':
                continue
            num = key[4:]
            gen_str += '''&%s {\n''' % (value.get_varName().lower())
            gen_str += '''\tcompatible = \"mediatek,%s-eint\";\n''' % (value.get_varName().lower())

            type = 1
            polarity = value.get_polarity()
            sensitive = value.get_sensitiveLevel()

            if polarity == 'High' and sensitive == 'Edge':
                type = 1
            elif polarity == 'Low' and sensitive == 'Edge':
                type = 2
            elif polarity == 'High' and sensitive == 'Level':
                type = 4
            elif polarity == 'Low' and sensitive == 'Level':
                type = 8

            gen_str += '''\tinterrupts = <%s %d>;\n''' % (num, type)
            gen_str += '''\tdebounce = <%s %d>;\n''' % (num, (int(value.get_debounceTime())) * 1000)
            gen_str += '''\tdedicated = <%s %d>;\n''' % (num, int(value.get_dedicatedEn()))
            if self.get_srcPinEnable():
                gen_str += '''\tsrc_pin = <%s %s>;\n''' % (num, self.get_srcPin()[value.get_srcPin()])
            else:
                gen_str += '''\tsrc_pin = <%s %s>;\n''' % (num, -1)
            gen_str += '''\tsockettype = <%s %s>;\n''' % (num, value.get_socketType())
            gen_str += '''\tstatus = \"okay\";\n'''
            gen_str += '''};\n'''

            gen_str += '''\n'''

        return gen_str

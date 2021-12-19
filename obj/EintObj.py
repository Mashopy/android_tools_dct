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
import os
import string

import configparser
import xml.dom.minidom

from data.EintData import EintData
from data.GpioData import GpioData
from utility.util import log
from utility.util import LogLevel
from utility.util import compare

from obj.ModuleObj import ModuleObj
from obj.GpioObj import GpioObj

class EintObj(ModuleObj):
    def __init__(self, gpio_obj):
        ModuleObj.__init__(self, 'cust_eint.h', 'cust_eint.dtsi')
        self.__gpio_obj = gpio_obj
        self.__count = 0
        self.__map_count = 0

    def set_gpioObj(self, gpio_obj):
        self.__gpio_obj = gpio_obj

    def read(self, node):
        nodes = node.childNodes

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

                data = EintData()
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

                ModuleObj.set_data(self, node.nodeName, data)

        return True

    def parse(self, node):
        self.get_cfgInfo()
        self.read(node)

    def gen_files(self):
        ModuleObj.gen_files(self)

    def gen_spec(self, para):
        ModuleObj.gen_spec(self, para)

    def get_cfgInfo(self):
        cp = configparser.ConfigParser(allow_no_value=True, strict=False)
        cp.read(ModuleObj.get_figPath())

        ops = cp.options('GPIO')
        map = {}
        mode_map = {}
        for op in ops:
            value = cp.get('GPIO', op)
            list = re.split(r' +|\t+', value)

            map[int(re.findall(r'\d+', op)[0])] = int(list[len(list)-2])
            mode_map[op] = list[0:len(list)-2]

        EintData.set_mapTable(map)
        EintData.set_modeMap(mode_map)

        if cp.has_option('EINT', 'EINT_MAP_COUNT'):
            self.__map_count = int(cp.get('EINT', 'EINT_MAP_COUNT'))

        if cp.has_option('EINT', 'INTERNAL_EINT'):
            info = cp.get('EINT', 'INTERNAL_EINT')
            str_list = info.split(':')
            for item in str_list:
                sub_list = item.split('/')
                EintData._int_eint[sub_list[0]] = sub_list[1]

        if cp.has_option('EINT', 'BUILTIN_EINT'):
            info = cp.get('EINT', 'BUILTIN_EINT')
            str_list = info.split(':')
            for builtin_item in str_list:
                builtin_list = builtin_item.split('/')
                #EintData._builtin_map[builtin_list[0]] = builtin_list[1]

                temp = 'BUILTIN_%s' %(builtin_list[0])
                if cp.has_option('EINT', temp):
                    info = cp.get('EINT', temp)
                    str_list = info.split(':')
                    temp_map = {}
                    for item in str_list:
                        sub_list = item.split('/')
                        temp_map[sub_list[0]] = sub_list[1] + ':' + builtin_list[1]

                    EintData._builtin_map[builtin_list[0]] = temp_map
                    EintData._builtin_eint_count += len(temp_map)

        self.__gpio_obj.set_eint_map_table(EintData._map_table)

    #def compare(self, value):
        #return string.atoi(value[4:])

    def fill_hFile(self):
        gen_str = ''
        gen_str += '''#ifdef __cplusplus\n'''
        gen_str += '''extern \"C\" {\n'''
        gen_str += '''#endif\n'''

        gen_str += '''#define CUST_EINTF_TRIGGER_RISING\t\t\t1\n'''
        gen_str += '''#define CUST_EINTF_TRIGGER_FALLING\t\t\t2\n'''
        gen_str += '''#define CUST_EINTF_TRIGGER_HIGH\t\t\t4\n'''
        gen_str += '''#define CUST_EINTF_TRIGGER_LOW\t\t\t8\n'''

        gen_str += '''#define CUST_EINT_DEBOUNCE_DISABLE\t\t\t0\n'''
        gen_str += '''#define CUST_EINT_DEBOUNCE_ENABLE\t\t\t1\n'''

        gen_str += '''\n\n'''

        sorted_list = sorted(ModuleObj.get_data(self).keys(), key=compare)

        for key in sorted_list:
            value = ModuleObj.get_data(self)[key]
            gen_str += '''#define CUST_EINT_%s_NUM\t\t\t%s\n''' %(value.get_varName().upper(), key[4:])
            gen_str += '''#define CUST_EINT_%s_DEBOUNCE_CN\t\t%s\n''' %(value.get_varName().upper(), value.get_debounceTime())

            temp = ''
            polarity = value.get_polarity()
            sensitive = value.get_sensitiveLevel()

            if polarity == 'High' and sensitive == 'Edge':
                temp = 'CUST_EINTF_TRIGGER_RISING'
            elif polarity == 'Low' and sensitive == 'Edge':
                temp = 'CUST_EINTF_TRIGGER_FALLING'
            elif polarity == 'High' and sensitive == 'Level':
                temp = 'CUST_EINTF_TRIGGER_HIGH'
            elif polarity == 'Low' and sensitive == 'Level':
                temp = 'CUST_EINTF_TRIGGER_LOW'

            gen_str += '''#define CUST_EINT_%s_TYPE\t\t\t%s\n''' %(value.get_varName().upper(), temp)

            temp = ''
            if value.get_debounceEnable() == 'Disable':
                temp = 'CUST_EINT_DEBOUNCE_DISABLE'
            elif value.get_debounceEnable() == 'Enable':
                temp = 'CUST_EINT_DEBOUNCE_ENABLE'
            gen_str += '''#define CUST_EINT_%s_DEBOUNCE_EN\t\t%s\n\n''' %(value.get_varName().upper(), temp)


        gen_str += '''#ifdef __cplusplus\n'''
        gen_str += '''}\n'''
        gen_str += '''#endif\n'''

        return gen_str

    def fill_mappingTable(self):
        gen_str = '''&eintc {\n'''
        count = 0

        if self.__map_count == 0:
            for i in range(0, int(self.__count)):
                if EintData.get_gpioNum(i) >= 0:
                    count += 1
            count += len(EintData._int_eint)
        else:
            count = self.__map_count

        gen_str += '''\tmediatek,mapping_table_entry = <%d>;\n''' %(count)
        gen_str += '''\t\t\t/* <gpio_pin, eint_pin> */\n'''
        gen_str += '''\tmediatek,mapping_table = '''

        sorted_list = sorted(EintData.get_mapTable().keys())
        for key in sorted_list:
            value = EintData.get_mapTable()[key]
            if value != -1:
                gen_str += '''<%d %d>,\n\t\t\t\t\t''' %(key, value)

        sorted_list = sorted(EintData.get_internalEint().keys())
        for key in sorted_list:
            value = EintData.get_internalEint()[key]
            gen_str += '''<%s %s>,\n\t\t\t\t\t''' %(value, key)
        #for (key, value) in EintData._int_eint.items():
            #gen_str += '''<%s %s>,\n\t\t\t\t\t''' %(value, key)

        gen_str = gen_str[0:len(gen_str)-7]
        gen_str += ''';\n'''
        gen_str += '''\tmediatek,builtin_entry = <%d>;\n''' %(EintData._builtin_eint_count)
        if len(EintData._builtin_map) == 0:
            gen_str += '''};\n\n'''
            return gen_str

        gen_str += '''\t\t\t\t\t/* gpio, built-in func mode, built-in eint */\n'''
        gen_str += '''\tmediatek,builtin_mapping = '''
        for (key, value) in EintData._builtin_map.items():
            for (sub_key, sub_value) in value.items():
                gen_str += '''<%s %s %s>, /* %s */\n\t\t\t\t\t''' %(sub_key, sub_value[0:1], key, sub_value)

        gen_str = gen_str[0:gen_str.rfind(',')]
        gen_str += ';'
        gen_str += '''};\n\n'''

        return gen_str

    def get_gpioNum(self, eint_num):
        for (key, value) in EintData.get_mapTable().items():
            if eint_num == value:
                return key

        return -1

    def refGpio(self, eint_num, flag):
        gpio_vec= []

        for key in EintData._builtin_map.keys():
            if int(eint_num) == int(key):
                temp_map = EintData._builtin_map[key]
                for key in temp_map.keys():
                    gpio_vec.append(key)

                if flag:
                    for item in temp_map.keys():
                        item_data = self.__gpio_obj.get_gpioData(int(item))

                        if item_data.get_defMode() == int(temp_map[item].split(':')[0]):
                            gpio_vec = []
                            gpio_vec.append(item)
                            return gpio_vec

                break

        gpio_num = EintData.get_gpioNum(int(eint_num))
        if gpio_num >= 0:
            gpio_vec.append(gpio_num)
            if flag:
                item_data = self.__gpio_obj.get_gpioData(gpio_num)
                mode_idx = item_data.get_defMode()
                mode_name = EintData.get_modeName(gpio_num, mode_idx)
                if re.match(r'GPIO[\d]+', mode_name) or re.match(r'EINT[\d]+', mode_name):
                    return gpio_vec

        return gpio_vec

    def fill_dtsiFile(self):
        gen_str = '''#include <dt-bindings/interrupt-controller/irq.h>\n'''
        gen_str += '''#include <dt-bindings/interrupt-controller/arm-gic.h>\n'''
        gen_str += '''\n'''

        gen_str += self.fill_mappingTable()

        sorted_list = sorted(ModuleObj.get_data(self).keys(), key=compare)

        for key in sorted_list:
            value = ModuleObj.get_data(self)[key]
            gen_str += '''&%s {\n''' %(value.get_varName().lower())
            gen_str += '''\tinterrupt-parent = <&eintc>;\n'''

            temp = ''
            polarity = value.get_polarity()
            sensitive = value.get_sensitiveLevel()

            if polarity == 'High' and sensitive == 'Edge':
                temp = 'IRQ_TYPE_EDGE_RISING'
            elif polarity == 'Low' and sensitive == 'Edge':
                temp = 'IRQ_TYPE_EDGE_FALLING'
            elif polarity == 'High' and sensitive == 'Level':
                temp = 'IRQ_TYPE_LEVEL_HIGH'
            elif polarity == 'Low' and sensitive == 'Level':
                temp = 'IRQ_TYPE_LEVEL_LOW'

            gen_str += '''\tinterrupts = <%s %s>;\n''' %(self.refGpio(key[4:], True)[0], temp)
            gen_str += '''\tdebounce = <%s %d>;\n''' %(self.refGpio(key[4:], True)[0], int(value.get_debounceTime()) * 1000)
            gen_str += '''\tstatus = \"okay\";\n'''
            gen_str += '''};\n'''
            gen_str += '''\n'''

        return gen_str

    def get_gpioObj(self):
        return self.__gpio_obj

class EintObj_MT6750S(EintObj):
    def __init__(self, gpio_obj):
        EintObj.__init__(self, gpio_obj)

    def parse(self, node):
        EintObj.parse(self, node)

    def gen_files(self):
        EintObj.gen_files(self)

    def gen_spec(self, para):
        EintObj.gen_spec(self, para)

    def fill_mappingTable(self):
        return ''

class EintObj_MT6739(EintObj):
    def __init__(self, gpio_obj):
        EintObj.__init__(self, gpio_obj)

    def fill_dtsiFile(self):
        gen_str = '''#include <dt-bindings/interrupt-controller/irq.h>\n'''
        gen_str += '''#include <dt-bindings/interrupt-controller/arm-gic.h>\n'''
        gen_str += '''\n'''

        gen_str += self.fill_mappingTable()

        sorted_list = sorted(ModuleObj.get_data(self).keys(), key=compare)

        for key in sorted_list:
            value = ModuleObj.get_data(self)[key]
            gen_str += '''&%s {\n''' % (value.get_varName().lower())
            gen_str += '''\tinterrupt-parent = <&pio>;\n'''

            temp = ''
            polarity = value.get_polarity()
            sensitive = value.get_sensitiveLevel()

            if polarity == 'High' and sensitive == 'Edge':
                temp = 'IRQ_TYPE_EDGE_RISING'
            elif polarity == 'Low' and sensitive == 'Edge':
                temp = 'IRQ_TYPE_EDGE_FALLING'
            elif polarity == 'High' and sensitive == 'Level':
                temp = 'IRQ_TYPE_LEVEL_HIGH'
            elif polarity == 'Low' and sensitive == 'Level':
                temp = 'IRQ_TYPE_LEVEL_LOW'

            gen_str += '''\tinterrupts = <%s %s %s %d>;\n''' % (key[4:], temp, self.refGpio(key[4:], True)[0], self.refGpio_defMode(key[4:], True))
            if value.get_debounceEnable() == 'Enable':
                gen_str += '''\tdeb-gpios = <&pio %s 0>;\n''' % (self.refGpio(key[4:], True)[0])
                gen_str += '''\tdebounce = <%d>;\n''' % (int(value.get_debounceTime()) * 1000)
            gen_str += '''\tstatus = \"okay\";\n'''
            gen_str += '''};\n'''
            gen_str += '''\n'''

        return gen_str

    def fill_mappingTable(self):
        return ''

    def refGpio_defMode(self, eint_num, flag):
        refGpio_defMode = 0

        for key in EintData._builtin_map.keys():
            if int(eint_num) == int(key):
                temp_map = EintData._builtin_map[key]

                if flag:
                    for item in temp_map.keys():
                        item_data = self.get_gpioObj().get_gpioData(int(item))

                        if item_data.get_defMode() == int(temp_map[item].split(':')[0]):
                            refGpio_defMode = item_data.get_defMode()
                            return refGpio_defMode

                break

        gpio_num = EintData.get_gpioNum(int(eint_num))
        if gpio_num >= 0:
            if flag:
                item_data = self.get_gpioObj().get_gpioData(gpio_num)
                refGpio_defMode = item_data.get_defMode()
                mode_name = EintData.get_modeName(gpio_num, refGpio_defMode)
                if re.match(r'GPIO[\d]+', mode_name) or re.match(r'EINT[\d]+', mode_name):
                    return refGpio_defMode

        return refGpio_defMode

class EintObj_MT6885(EintObj_MT6739):
    def fill_hFile(self):
	    gen_str = ''
	    gen_str += '''#ifdef __cplusplus\n'''
	    gen_str += '''extern \"C\" {\n'''
	    gen_str += '''#endif\n'''
	    gen_str += '''#define CUST_EINTF_TRIGGER_RISING\t\t\t1\n'''
	    gen_str += '''#define CUST_EINTF_TRIGGER_FALLING\t\t\t2\n'''
	    gen_str += '''#define CUST_EINTF_TRIGGER_HIGH\t\t\t4\n'''
	    gen_str += '''#define CUST_EINTF_TRIGGER_LOW\t\t\t8\n'''
	    gen_str += '''#define CUST_EINT_DEBOUNCE_DISABLE\t\t\t0\n'''
	    gen_str += '''#define CUST_EINT_DEBOUNCE_ENABLE\t\t\t1\n'''
	    gen_str += '''\n\n'''

	    sorted_list = sorted(ModuleObj.get_data(self).keys(), key=compare)
	    for key in sorted_list:
	        value = ModuleObj.get_data(self)[key]
	        gen_str += '''#define CUST_EINT_%s_NUM\t\t\t%s\n''' %(value.get_varName().upper(), key[4:])
	        if int(key[4:]) < 32:
	            gen_str += '''#define CUST_EINT_%s_DEBOUNCE_CN\t\t%s\n''' %(value.get_varName().upper(), value.get_debounceTime())

	        temp = ''
	        polarity = value.get_polarity()
	        sensitive = value.get_sensitiveLevel()

	        if polarity == 'High' and sensitive == 'Edge':
	            temp = 'CUST_EINTF_TRIGGER_RISING'
	        elif polarity == 'Low' and sensitive == 'Edge':
	            temp = 'CUST_EINTF_TRIGGER_FALLING'
	        elif polarity == 'High' and sensitive == 'Level':
	            temp = 'CUST_EINTF_TRIGGER_HIGH'
	        elif polarity == 'Low' and sensitive == 'Level':
	            temp = 'CUST_EINTF_TRIGGER_LOW'

	        gen_str += '''#define CUST_EINT_%s_TYPE\t\t\t%s\n''' %(value.get_varName().upper(), temp)

	        temp = ''
	        if value.get_debounceEnable() == 'Disable':
	            temp = 'CUST_EINT_DEBOUNCE_DISABLE'
	        elif value.get_debounceEnable() == 'Enable':
	            temp = 'CUST_EINT_DEBOUNCE_ENABLE'
	        gen_str += '''#define CUST_EINT_%s_DEBOUNCE_EN\t\t%s\n\n''' %(value.get_varName().upper(), temp)

	    gen_str += '''#ifdef __cplusplus\n'''
	    gen_str += '''}\n'''
	    gen_str += '''#endif\n'''
	    return gen_str

    def fill_dtsiFile(self):
        gen_str = '''#include <dt-bindings/interrupt-controller/irq.h>\n'''
        gen_str += '''#include <dt-bindings/interrupt-controller/arm-gic.h>\n'''
        gen_str += '''\n'''

        gen_str += self.fill_mappingTable()

        sorted_list = sorted(ModuleObj.get_data(self).keys(), key=compare)
        for key in sorted_list:
            value = ModuleObj.get_data(self)[key]
            gen_str += '''&%s {\n''' % (value.get_varName().lower())
            gen_str += '''\tinterrupt-parent = <&pio>;\n'''

            temp = ''
            polarity = value.get_polarity()
            sensitive = value.get_sensitiveLevel()

            if polarity == 'High' and sensitive == 'Edge':
                temp = 'IRQ_TYPE_EDGE_RISING'
            elif polarity == 'Low' and sensitive == 'Edge':
                temp = 'IRQ_TYPE_EDGE_FALLING'
            elif polarity == 'High' and sensitive == 'Level':
                temp = 'IRQ_TYPE_LEVEL_HIGH'
            elif polarity == 'Low' and sensitive == 'Level':
                temp = 'IRQ_TYPE_LEVEL_LOW'

            gen_str += '''\tinterrupts = <%s %s %s %d>;\n''' % (key[4:], temp, self.refGpio(key[4:], True)[0], self.refGpio_defMode(key[4:], True))
            if value.get_debounceEnable() == 'Enable':
                gen_str += '''\tdeb-gpios = <&pio %s 0>;\n''' % (self.refGpio(key[4:], True)[0])
                # from MT6885, only 0 ~ 31 eint gen debounce time item
                if int(key[4:]) < 32:
                    gen_str += '''\tdebounce = <%d>;\n''' % (int(value.get_debounceTime()) * 1000)
            gen_str += '''\tstatus = \"okay\";\n'''
            gen_str += '''};\n'''
            gen_str += '''\n'''
        return gen_str

class EintObj_MT6853(EintObj_MT6885):
    def fill_dtsiFile(self):
        gen_str = '''#include <dt-bindings/interrupt-controller/irq.h>\n'''
        gen_str += '''#include <dt-bindings/interrupt-controller/arm-gic.h>\n'''
        gen_str += '''\n'''

        gen_str += self.fill_mappingTable()

        sorted_list = sorted(ModuleObj.get_data(self).keys(), key=compare)
        for key in sorted_list:
            value = ModuleObj.get_data(self)[key]
            gen_str += '''&%s {\n''' % (value.get_varName().lower())
            gen_str += '''\tinterrupt-parent = <&pio>;\n'''

            temp = ''
            polarity = value.get_polarity()
            sensitive = value.get_sensitiveLevel()

            if polarity == 'High' and sensitive == 'Edge':
                temp = 'IRQ_TYPE_EDGE_RISING'
            elif polarity == 'Low' and sensitive == 'Edge':
                temp = 'IRQ_TYPE_EDGE_FALLING'
            elif polarity == 'High' and sensitive == 'Level':
                temp = 'IRQ_TYPE_LEVEL_HIGH'
            elif polarity == 'Low' and sensitive == 'Level':
                temp = 'IRQ_TYPE_LEVEL_LOW'

            gen_str += '''\tinterrupts = <%s %s>;\n''' % (key[4:], temp)
            if value.get_debounceEnable() == 'Enable':
                gen_str += '''\tdeb-gpios = <&pio %s 0>;\n''' % (self.refGpio(key[4:], True)[0])
                # from MT6885, only 0 ~ 31 eint gen debounce time item
                if int(key[4:]) < 32:
                    gen_str += '''\tdebounce = <%d>;\n''' % (int(value.get_debounceTime()) * 1000)
            gen_str += '''\tstatus = \"okay\";\n'''
            gen_str += '''};\n'''
            gen_str += '''\n'''
        return gen_str

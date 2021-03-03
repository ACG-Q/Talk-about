#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os

# ----------文件路径--------------------
SYSFS_GPIO_DIR = "/sys/class/gpio"
GPIO_EXPORT_PATH = SYSFS_GPIO_DIR + '/export'
GPIO_UNEXPORT_PATH = SYSFS_GPIO_DIR + '/unexport'
GPIO_DIR_PATH = SYSFS_GPIO_DIR + '/gpio%d/direction'
GPIO_VAL_PATH = SYSFS_GPIO_DIR + f'/gpio%d/value'
GPIO_EDGE_PATH = SYSFS_GPIO_DIR + f'/gpio%d/edge'

# 相关参数
RISING = "rising" # 设置上升(rising)
FALLING = "falling" # 设置下降(falling)
BOTH = "both" # 设置上升(both)
INPUT = 'in'
OUTPUT = 'out'
HIGHT = '1'
LOW = '0'


# ****************************************************************
# * gpio_export 导出GPIO配置
# * echo 132 > /sys/class/gpio/export
# ****************************************************************
def gpio_export(gpio):
    """
    导出GPIO配置
    :param gpio:引脚
    :return: True 导出GPIO文件成功 False 已存在GPIO文件 or 导出失败
    """
    if not os.path.exists(SYSFS_GPIO_DIR + f'/gpio{gpio}'):
        try:
            fd = os.popen(f'echo {gpio} >' + GPIO_EXPORT_PATH)
            fd.close()
            return True
        except:
            return False
    else:
        return False


# ****************************************************************
# * gpio_unexport 删除GPIO配置
# * echo 132 > /sys/class/gpio/unexport
# ****************************************************************
def gpio_unexport(gpio):
    """
    删除GPIO配置
    :param gpio: 引脚
    :return:True 删除GPIO配置文件成功 Fasle 失败
    """
    try:
        fd = os.popen(f'echo {gpio} >' + GPIO_UNEXPORT_PATH)
        fd.close()
        return True
    except:
        return False


# ****************************************************************
# * gpio_set_dir 设置输入输出
# * echo out > /sys/class/gpio/gpio132/direction
# * echo in > /sys/class/gpio/gpio133/direction
# ****************************************************************
def gpio_set_dir(gpio, flag):
    """
    设置输入输出
    :param gpio: 引脚
    :param flag: INPUT/OUTPUT
    :return:True 设置成功  False设置失败
    """
    if not flag in [INPUT,OUTPUT]:
        print('gpio_set_dir no have %s'%flag)
        exit()
    try:
        fd = os.popen(f'echo {flag} >' + GPIO_DIR_PATH % gpio, 'r')
        fd.close()
        return True
    except:
        return False


# ****************************************************************
# * gpio_set_value 设置高低电平
# * echo 1 > /sys/class/gpio/gpio132/value # 设置GPIO输出高电平
# * echo 0 > /sys/class/gpio/gpio132/value # 设置GPIO输出低电平
# ****************************************************************
def gpio_set_value(gpio, value):
    """
    设置高低电平
    :param gpio:引脚
    :param value:电平值
    :return:True 设置成功 False 设置失败
    """
    if not value in [HIGHT,LOW]:
        print('gpio_set_value no have %s'%value)
        exit()
    try:
        fd = os.popen(f'echo {value} >' + GPIO_VAL_PATH % gpio)
        fd.close()
        return True
    except:
        return False

# ****************************************************************
# * gpio_get_value 获取电平
# * cat /sys/class/gpio/gpio133/value
# ****************************************************************
def gpio_get_value(gpio):
    """
    获取电平
    :param gpio: 引脚
    :return: 电平 0 or 1
    """
    fd = os.popen('cat ' + GPIO_VAL_PATH % gpio, 'r')
    fd.close()
    return fd.read()


# ****************************************************************
# * gpio_set_edge 设置边缘中断触发事件
# ****************************************************************
def gpio_set_edge(gpio, edge):
    """
    设置边缘中断触发事件
    :param gpio:引脚
    :param edge:边缘事件
    :return:True 设置成功 False 设置失败
    """
    if not edge in [RISING,FALLING,BOTH]:
        print('gpio_set_edge no have %s'%edge)
        exit()
    try:
        fd =  os.popen(f'echo {edge} >' + GPIO_EDGE_PATH % gpio)
        fd.close()
        return True
    except:
        return False


# ****************************************************************
# * gpio_fd_open
# ****************************************************************
def gpio_fd_open(gpio):
    """
    打开value文件
    :param gpio: 引脚
    :return: 包含信息描述符的信息对象
    """
    fd = open(GPIO_VAL_PATH % gpio,'r')
    if fd.fileno() < 0:
        print('fd error')
        exit()
    return fd


# ****************************************************************
# * gpio_fd_close
# ****************************************************************
def gpio_fd_close(fd):
    """
    关闭信息对象
    :param fd:信息对象
    """
    fd.close()
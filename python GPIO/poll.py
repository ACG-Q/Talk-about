from GPIO import *
import select
TIMEOUT = 3

def main(argv):
    gpio = int(argv)  # 将GPIO(str) -> GPIO(int)

    gpio_export(gpio)  # 导出GPIO配置
    gpio_set_dir(gpio, INPUT)  # 设置输入
    gpio_set_edge(gpio, RISING)  # 设置上升(rising)
    # gpio_set_edge(gpio, FALLING) # 设置下降(falling)
    # gpio_set_edge(gpio, BOTH) # 设置变化(both)
    gpio_fd = gpio_fd_open(gpio)  # 获取/sys/gpio/gpio{gpio}/value --> 电平值

    pl = select.poll()
    pl.register(gpio_fd.fileno(), select.POLLPRI)
    while True:
        for fd, event in pl.poll(TIMEOUT):
            if not event & select.POLLPRI:
                continue
            print(gpio_fd.read())
            gpio_fd.seek(0)


main(57)
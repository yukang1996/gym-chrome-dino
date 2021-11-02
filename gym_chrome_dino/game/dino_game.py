#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

from gym_chrome_dino.utils.helpers import download_chromedriver


class DinoGame:
    def __init__(self, render=False, accelerate=False, autoscale=False):
        if not os.path.exists('chromedriver') and not os.path.exists('chromedriver.exe'):
            download_chromedriver()
        chromedriver_path = './chromedriver'
        options = Options()
        options.add_argument('--disable-infobars')
        options.add_argument('--mute-audio')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=800,600')
        if not render:
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)

        # Get Dino URL to render according to ENV Variable DINO_PATH

        dino_url = str(os.environ.get("DINO_URL", "chrome://dino"))

        try:
            self.driver.get(dino_url)
        except WebDriverException:
            pass

        self.defaults = self.get_parameters()  # default parameters
        if not accelerate:
            self.set_parameter('config.ACCELERATION', 0)
        if not autoscale:
            self.driver.execute_script('Runner.instance_.setArcadeModeContainerScale = function(){};')
        self.press_space()

    def get_parameters(self):
        params = {'config.ACCELERATION': self.driver.execute_script('return Runner.config.ACCELERATION;')}
        return params

    def is_crashed(self):
        return self.driver.execute_script('return Runner.instance_.crashed;')

    def is_inverted(self):
        return self.driver.execute_script('return Runner.instance_.inverted;')

    def is_paused(self):
        return self.driver.execute_script('return Runner.instance_.paused;')

    def is_playing(self):
        return self.driver.execute_script('return Runner.instance_.playing;')

    def press_space(self):
        return self.driver.find_element_by_tag_name('body').send_keys(Keys.SPACE)

    def press_up(self):
        return self.driver.find_element_by_tag_name('body').send_keys(Keys.UP)

    def press_down(self):
        return self.driver.find_element_by_tag_name('body').send_keys(Keys.DOWN)

    def pause(self):
        return self.driver.execute_script('Runner.instance_.stop();')

    def resume(self):
        return self.driver.execute_script('Runner.instance_.play();')

    def restart(self):
        return self.driver.execute_script('Runner.instance_.restart();')

    def close(self):
        self.driver.close()

    def get_score(self):
        digits = self.driver.execute_script('return Runner.instance_.distanceMeter.digits;')
        return int(''.join(digits))

    def get_dino_x_position(self):
        return self.driver.execute_script('return Runner.instance_.tRex.xPos;')

    def get_dino_y_position(self):
        return self.driver.execute_script('return Runner.instance_.tRex.yPos;')

    def get_nth_nearest_obstacle_width(self, n):
        return self.driver.execute_script(
            'return Runner'
            f'.instance_.horizon.obstacles.length ? Runner.instance_.horizon.obstacles[{ n - 1 }].typeConfig.width : 0')

    def get_nth_nearest_obstacle_height(self, n):
        return self.driver.execute_script(
            'return Runner.instance_.horizon.obstacles.length ? '
            f'Runner.instance_.horizon.obstacles[{ n - 1 }].typeConfig.height : 0')

    def get_nth_nearest_obstacle_x_distance(self, n):
        t_nearest_obstacle = self.driver.execute_script(
            'return Runner'
            f'.instance_.horizon.obstacles.length ? Runner.instance_.horizon.obstacles[{ n - 1 }].xPos : 600')
        return t_nearest_obstacle - self.get_dino_x_position()

    def get_nth_nearest_obstacle_y_distance(self, n):
        t_nearest_obstacle = self.driver.execute_script(
            'return Runner'
            f'.instance_.horizon.obstacles.length ? Runner.instance_.horizon.obstacles[{ n - 1 }].yPos : 150')
        return t_nearest_obstacle - self.get_dino_y_position()

    def get_speed(self):
        return self.driver.execute_script('return Runner.instance_.currentSpeed;')

    def get_canvas(self):
        return self.driver.execute_script(
            'return document.getElementsByClassName("runner-canvas")[0].toDataURL().substring(22);')

    def set_parameter(self, key, value):
        self.driver.execute_script('Runner.{} = {};'.format(key, value))

    def restore_parameter(self, key):
        self.set_parameter(key, self.defaults[key])

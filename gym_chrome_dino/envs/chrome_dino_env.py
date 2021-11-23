#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import base64
import io

import gym
import numpy as np
from PIL import Image
from gym import spaces
import cv2  # opencv

from gym_chrome_dino.game import DinoGame
from gym_chrome_dino.utils.helpers import rgba2rgb
from statistics import mean


class ChromeDinoEnv(gym.Env):
    metadata = {'render.modes': ['rgb_array'], 'video.frames_per_second': 10}

    def __init__(self, render, accelerate, autoscale):
        self.game = DinoGame(render, accelerate)
        image_size = self._observe().shape
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(80, 80), dtype=np.uint8
        )
        self.action_space = spaces.Discrete(2)
        self.gametime_reward = 0.1
        self.gameover_penalty = -1
        self.current_frame = self.observation_space.low
        self._action_set = [0, 1, 2]

    def _observe(self):
        s = self.game.get_canvas()
        b = io.BytesIO(base64.b64decode(s))
        i = Image.open(b)
        i = rgba2rgb(i)
        a = np.array(i)
        self.current_frame = self.process_img(a)

        return self.current_frame

    def step(self, action):
        if action == 1:
            self.game.press_up()
        if action == 2:
            self.game.press_down()
        if action == 3:
            self.game.press_space()
        observation = self._observe()
        reward = self.gametime_reward
        done = False
        info = {}
        if self.game.is_crashed():
            reward = self.gameover_penalty
            done = True
        return observation, reward, done, info

    def reset(self, record=False):
        self.game.restart()
        return self._observe()

    def render(self, mode='rgb_array', close=False):
        assert mode == 'rgb_array', 'Only supports rgb_array mode.'
        return self.current_frame

    def close(self):
        self.game.close()

    def get_score(self):
        return self.game.get_score()

    def set_acceleration(self, enable):
        if enable:
            self.game.restore_parameter('config.ACCELERATION')
        else:
            self.game.set_parameter('config.ACCELERATION', 0)

    def get_action_meanings(self):
        return [ACTION_MEANING[i] for i in self._action_set]

    def process_img(self, image):

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # RGB to Grey Scale
        image = image[:300, :500]  # Crop Region of Interest(ROI)
        image = cv2.resize(image, (80, 80)) # Reduce the dimension

        return image

class ChromeDinoGAEnv(gym.Env):
    metadata = {'render.modes': ['rgb_array'], 'video.frames_per_second': 10}

    def __init__(self, render, accelerate, autoscale, input_mode):

        self.game = DinoGame(render, accelerate)

        if input_mode == 'one_obstacle':

            """
                Limits of observation space:

                dino_position_x => [0, 600]
                dino_position_y => [0, 150]
                1st_obstacle_x_distance => [-20, 600]
                1st_obstacle_y_distance => [-20, 150]
                1st_obstacle_width => [0, 200]
                1st_obstacle_height => [0, 100]
                speed => [0, 100]

            """

            self.observation_space = spaces.Box(
                low=np.array([0.0, 0.0, -20.0, -20.0, 0.0, 0.0, 0.0]),
                high=np.array([600.0, 150.0, 600.0, 150.0, 600.0, 150.0, 100.0]),
                dtype=np.float32
            )

        elif input_mode == 'two_obstacle':

            """
                Limits of observation space:
    
                dino_position_x => [0, 600]
                dino_position_y => [0, 150]
                1st_obstacle_x_distance => [-20, 600]
                1st_obstacle_y_distance => [-20, 150]
                1st_obstacle_width => [0, 200]
                1st_obstacle_height => [0, 100]
                2nd_obstacle_x_distance => [-20, 600]
                2nd_obstacle_y_distance => [-20, 150]
                2nd_obstacle_width => [0, 200]
                2nd_obstacle_height => [0, 100]
                speed => [0, 100]
    
            """

            self.observation_space = spaces.Box(
                low=np.array([0.0, 0.0, -20.0, -20.0, 0.0, 0.0, -20.0, -20.0, 0.0, 0.0, 0.0]),
                high=np.array([600.0, 150.0, 600.0, 150.0, 600.0, 150.0, 600.0, 150.0, 200.0, 100.0, 100.0]),
                dtype=np.float32
            )

        else:

            raise Exception("Unsupported input mode, type: 'one_obstacle' or 'two_obstacle'")

        self.action_space = spaces.Discrete(3)
        self.gametime_reward = 0.1
        self.gameover_penalty = -1
        self.score_mode = 'penalization'
        self.input_mode = input_mode
        self.current_frame = self.observation_space.low
        self._action_set = [0, 1, 2]

    def _observe(self):

        if self.input_mode == 'one_obstacle':

            dino_position_x = float(self.game.get_dino_x_position())
            dino_position_y = float(self.game.get_dino_y_position())
            first_obstacle_x_distance = float(self.game.get_nth_nearest_obstacle_x_distance(1))
            first_obstacle_y_distance = float(self.game.get_nth_nearest_obstacle_y_distance(1))
            first_obstacle_width = float(self.game.get_nth_nearest_obstacle_width(1))
            first_obstacle_height = float(self.game.get_nth_nearest_obstacle_height(1))
            speed = float(self.game.get_speed())

            self.current_frame = np.array([
                dino_position_x / mean([self.observation_space.low[0], self.observation_space.high[0]]),
                dino_position_y / mean([self.observation_space.low[1], self.observation_space.high[1]]),
                first_obstacle_x_distance / mean([self.observation_space.low[2], self.observation_space.high[2]]),
                first_obstacle_y_distance / mean([self.observation_space.low[3], self.observation_space.high[3]]),
                first_obstacle_width / mean([self.observation_space.low[4], self.observation_space.high[4]]),
                first_obstacle_height / mean([self.observation_space.low[5], self.observation_space.high[5]]),
                speed / mean([self.observation_space.low[6], self.observation_space.high[6]]),
            ])

        elif self.input_mode == 'two_obstacle':

            dino_position_x = float(self.game.get_dino_x_position())
            dino_position_y = float(self.game.get_dino_y_position())
            first_obstacle_x_distance = float(self.game.get_nth_nearest_obstacle_x_distance(1))
            first_obstacle_y_distance = float(self.game.get_nth_nearest_obstacle_y_distance(1))
            first_obstacle_width = float(self.game.get_nth_nearest_obstacle_width(1))
            first_obstacle_height = float(self.game.get_nth_nearest_obstacle_height(1))
            second_obstacle_x_distance = float(self.game.get_nth_nearest_obstacle_x_distance(1))
            second_obstacle_y_distance = float(self.game.get_nth_nearest_obstacle_y_distance(1))
            second_obstacle_width = float(self.game.get_nth_nearest_obstacle_width(1))
            second_obstacle_height = float(self.game.get_nth_nearest_obstacle_height(1))
            speed = float(self.game.get_speed())

            self.current_frame = np.array([
                dino_position_x / mean([self.observation_space.low[0], self.observation_space.high[0]]),
                dino_position_y / mean([self.observation_space.low[1], self.observation_space.high[1]]),
                first_obstacle_x_distance / mean([self.observation_space.low[2], self.observation_space.high[2]]),
                first_obstacle_y_distance / mean([self.observation_space.low[3], self.observation_space.high[3]]),
                first_obstacle_width / mean([self.observation_space.low[4], self.observation_space.high[4]]),
                first_obstacle_height / mean([self.observation_space.low[5], self.observation_space.high[5]]),
                second_obstacle_x_distance / mean([self.observation_space.low[6], self.observation_space.high[6]]),
                second_obstacle_y_distance / mean([self.observation_space.low[7], self.observation_space.high[7]]),
                second_obstacle_width / mean([self.observation_space.low[8], self.observation_space.high[8]]),
                second_obstacle_height / mean([self.observation_space.low[9], self.observation_space.high[9]]),
                speed / mean([self.observation_space.low[10], self.observation_space.high[10]]),
            ])

        return self.current_frame

    def step(self, action):
        if action == 1:
            self.game.press_up()
        if action == 2:
            self.game.press_down()
        if action == 3:
            self.game.press_space()
        observation = self._observe()
        reward = self.gametime_reward if self.score_mode == 'penalization' else self.get_score()
        done = False
        info = {}
        if self.game.is_crashed():
            reward = self.gameover_penalty if self.score_mode == 'penalization' else reward
            done = True
        return observation, reward, done, info

    def reset(self, record=False):
        self.game.restart()
        return self._observe()

    def render(self, mode='rgb_array', close=False):
        assert mode == 'rgb_array', 'Only supports rgb_array mode.'
        return self.current_frame

    def close(self):
        self.game.close()

    def get_score(self):
        return self.game.get_score()

    def set_acceleration(self, enable):
        if enable:
            self.game.restore_parameter('config.ACCELERATION')
        else:
            self.game.set_parameter('config.ACCELERATION', 0)

    def get_action_meanings(self):
        return [ACTION_MEANING[i] for i in self._action_set]

    def set_score_mode(self, type):

        if type == 'normal' or type == 'penalization':
            self.score_mode = type
        else:
            raise Exception("Unsupported score mode, type: 'normal' or 'penalization'")


ACTION_MEANING = {
    0: "NOOP",
    1: "UP",
    2: "DOWN",
    3: "SPACE",
}

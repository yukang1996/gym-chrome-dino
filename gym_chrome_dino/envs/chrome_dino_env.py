#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import base64
import io
import numpy as np
import os
from collections import deque
from PIL import Image

import gym
from gym import error, spaces, utils
from gym.utils import seeding

from gym_chrome_dino.game import DinoGame
from gym_chrome_dino.utils.helpers import rgba2rgb


class ChromeDinoEnv(gym.Env):
    metadata = {'render.modes': ['rgb_array'], 'video.frames_per_second': 10}

    def __init__(self, render, accelerate, autoscale):
        self.game = DinoGame(render, accelerate)
        image_size = self._observe().shape
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(150, 600, 3), dtype=np.uint8
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
        self.current_frame = a
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


class ChromeDinoGAEnv(gym.Env):
    metadata = {'render.modes': ['rgb_array'], 'video.frames_per_second': 10}

    def __init__(self, render, accelerate, autoscale):
        self.game = DinoGame(render, accelerate)

        """
            Limits of observation space:
            
            obstacle_x_distance => [-20, 600]
            obstacle_y_distance => [-20, 150]
            dino_position_x => [0, 600]
            dino_position_y => [0, 150]
            next_obstacle_width => [0, 200]
            next_obstacle_height => [0, 100]
            speed => [0, 100]
            
        """

        self.observation_space = spaces.Box(
            low=np.array([-20.0, -20.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            high=np.array([600.0, 150.0, 600.0, 150.0, 200.0, 100.0, 100.0]),
            dtype=np.float32
        )

        self.action_space = spaces.Discrete(3)
        self.gametime_reward = 0.1
        self.gameover_penalty = -1
        self.current_frame = self.observation_space.low
        self._action_set = [0, 1, 2]

    def _observe(self):

        obstacle_x_distance = float(self.game.get_nearest_obstacle_x_distance())
        obstacle_y_distance = float(self.game.get_nearest_obstacle_y_distance())
        dino_position_x = float(self.game.get_dino_x_position())
        dino_position_y = float(self.game.get_dino_y_position())
        next_obstacle_width = float(self.game.get_nearest_obstacle_width())
        next_obstacle_height = float(self.game.get_nearest_obstacle_height())
        speed = float(self.game.get_speed())

        self.current_frame = np.array([
            obstacle_x_distance,
            obstacle_y_distance,
            dino_position_x,
            dino_position_y,
            next_obstacle_width,
            next_obstacle_height,
            speed
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
        # reward = self.gametime_reward
        done = False
        info = {}
        if self.game.is_crashed():
            # reward = self.gameover_penalty
            done = True
        reward = self.game.get_score()
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


ACTION_MEANING = {
    0: "NOOP",
    1: "UP",
    2: "DOWN",
    3: "SPACE",
}

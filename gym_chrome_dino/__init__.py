#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

from gym.envs.registration import register

register(
    id='ChromeDino-v0',
    entry_point='gym_chrome_dino.envs:ChromeDinoEnv',
    kwargs={'render': True, 'accelerate': True}
)

register(
    id='ChromeDinoGAOneObstacle-v0',
    entry_point='gym_chrome_dino.envs:ChromeDinoGAEnv',
    kwargs={'render': True, 'accelerate': True, 'input_mode': 'one_obstacle'}
)

register(
    id='ChromeDinoGATwoObstacle-v0',
    entry_point='gym_chrome_dino.envs:ChromeDinoGAEnv',
    kwargs={'render': True, 'accelerate': True, 'input_mode': 'two_obstacle'}
)

register(
    id='ChromeDinoNoBrowser-v0',
    entry_point='gym_chrome_dino.envs:ChromeDinoEnv',
    kwargs={'render': False, 'accelerate': False}
)

register(
    id='ChromeDinoGAOneObstacleNoBrowser-v0',
    entry_point='gym_chrome_dino.envs:ChromeDinoGAEnv',
    kwargs={'render': False, 'accelerate': True, 'input_mode': 'one_obstacle'}
)

register(
    id='ChromeDinoGATwoObstacleNoBrowser-v0',
    entry_point='gym_chrome_dino.envs:ChromeDinoGAEnv',
    kwargs={'render': False, 'accelerate': True, 'input_mode': 'two_obstacle'}
)


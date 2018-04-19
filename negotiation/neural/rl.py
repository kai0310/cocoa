import argparse
import random
import json
import numpy as np
import pdb

from core.controller import Controller

def add_rl_arguments(parser):
    group = parser.add_argument_group('Reinforce')
    group.add_argument('--max-turns', default=100, type=int, help='Maximum number of turns')
    group.add_argument('--num-dialogues', default=10000, type=int,
            help='Number of dialogues to generate/train')
    group.add_argument('--discount_factor', default=0.95, type=float,
            help='Amount to discount the reward for each timestep when \
            calculating the value, usually written as gamma')
    group.add_argument('--verbose', default=False, action='store_true',
            help='Whether or not to have verbose prints')

    group = parser.add_argument_group('Training')
    group.add_argument('--optim', default='sgd', help="""Optimization method.""",
                       choices=['sgd', 'adagrad', 'adadelta', 'adam'])


class Reinforce(object):
    def __init__(self, agents, scenarios):
        self.agents = agents
        self.scenarios = scenarios

    def _get_controller(self):
        scenario = random.choice(self.scenarios)
        # Randomize because kb[0] is always seller
        if random.random() < 0.5:
            kbs = (scenario.kbs[0], scenario.kbs[1])
        else:
            kbs = (scenario.kbs[1], scenario.kbs[0])
        sessions = [self.agents[0].new_session(0, kbs[0], rl=True),
                    self.agents[1].new_session(1, kbs[1], rl=False)]
        return Controller(scenario, sessions)

    def get_reward(self, example):
        # reward = reward if agree else 0
        # self.all_rewards.append(reward)
        # standardize the reward
        # r = (reward - np.mean(self.all_rewards)) / max(1e-4, np.std(self.all_rewards))
        pdb.set_trace()
        # check what is in agents, and what is in scenario

        if not self.agent.has_deal(example.outcome):
            return 0   # there is no reward if there is no valid outcome
        reward = example.outcome['reward']
        offer = example.outcome['offer']

        margins = {'seller': 0, 'buyer': 0}
        targets = {}
        # for agent in agents?
        for role in ('seller', 'buyer'):
            # kb comes from scenario?
            targets[role] = self.kb_by_role[role].facts["personal"]["Target"]
        midpoint = (targets['seller'] + targets['buyer']) / 2.
        price = self.outcome['offer']['price']

        norm_factor = abs(midpoint - targets['seller'])
        margins['seller'] = (price - midpoint) / norm_factor
        # Zero sum
        margins['buyer'] = -1. * margins['seller']
        return margins

    def learn(self, opt):
        for i in xrange(opt.num_dialogues):
            controller = self._get_controller()
            example = controller.simulate(max_turns, verbose=args.verbose)
            rewards = self.get_reward(example)
            for session in controller.sessions:
                if hasattr(session, 'trainable') and session.trainable:
                    session.update(reward)
            # TODO: logging

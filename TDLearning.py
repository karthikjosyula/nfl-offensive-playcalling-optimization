"""Implement TD learning on NFL playcalling data"""
import collections
from tensorboardX import SummaryWriter
import numpy as np
from TDEnv import NFLPlaycallingEnvTD

GAMMA = 0.95    # A discount rate. A value between 0 and 1. The higher the value the less you are discounting
ALPHA = 0.05    # The learning rate. Value between 0 and 1.
                # How much the error should we accept and therefore adjust our estimates towards.
LAMBDA = 0.6    # The credit assignment variable. Value between 0 and 1.
                # The more credit you assign to further back states and actions
DELTA = 0       # A change or difference in value. Would be updated in runtime.
TEST_EPISODES = 80

def random_play(environment, count, render=False):
    for ep in range(count):
        total_reward = 0.0
        total_steps = 0
        obs = environment.reset()

        while True:
            action = environment.action_space.sample()
            obs, reward, done, _ = environment.step(action)

            if render:
                env.render()

            total_reward += reward
            total_steps += 1
            if done:
                break

        print("Episode done in {} steps with {:.2f} reward".format(total_steps, total_reward))


class Agent:
    def __init__(self, environment):
        self.env = environment
        self.state = self.env.reset()
        self.rewards = collections.defaultdict(float)
        self.transits = collections.defaultdict(collections.Counter)
        self.values = collections.defaultdict(float)

    def play_n_random_steps(self, count):
        for _ in range(count):
            action = self.env.action_space.sample()
            new_state, reward, is_done, _ = self.env.step(action)
            self.rewards[(self.state, action, new_state)] = reward
            self.transits[(self.state, action)][new_state] += 1
            self.state = self.env.reset() if is_done else new_state

    def calc_action_value(self, state, action):
        target_counts = self.transits[(state, action)]
        #total = sum(target_counts.values())
        action_value = 0.0
        for tgt_state, count in target_counts.items():
            reward = self.rewards[(state, action, tgt_state)]
            DELTA = reward+GAMMA*self.values[tgt_state] - action_value
            action_value+= (ALPHA * DELTA)
        return action_value

    def select_action(self, state):
        best_action, best_value = None, None
        for action in range(self.env.action_space.n):
            action_value = self.values[(state, action)]
            if best_value is None or best_value < action_value:
                best_value = action_value
                best_action = action
        return best_action

    def play_episode(self, env):
        total_reward = 0.0
        state = env.reset()
        while True:
            action = self.select_action(state)
            new_state, reward, is_done, _ = env.step(action)
            self.rewards[(state, action, new_state)] = reward
            self.transits[(state, action)][new_state] += 1
            total_reward += reward
            if is_done:
                break
            state = new_state
        return total_reward

    def value_iteration(self):
        for state in range(env.observation_space.n):
            state_values = [self.calc_action_value(state, action) for action in range(env.action_space.n)]
            self.values[state] = max(state_values)

    def evaluation(self, state):
        print('=====================================')
        print('Evaluation')
        print('=====================================')
        eval_action = self.select_action(state)
        print(f'For state: {state}, action is {eval_action}')

if __name__ == '__main__':
    env = NFLPlaycallingEnvTD()
    # random_play(env)
    test_env = env
    agent = Agent(environment=NFLPlaycallingEnvTD())
    writer = SummaryWriter(comment="-TD-learning")

    iter_no = 0
    best_reward = -7.0
    while True:
        iter_no += 1
        print('=====================================')
        print('Exploration')
        agent.play_n_random_steps(100)
        print('=====================================')
        print('Exploitation')
        agent.value_iteration()

        reward = 0.0
        for _ in range(TEST_EPISODES):
            reward += agent.play_episode(test_env)
        reward /= TEST_EPISODES
        writer.add_scalar("reward", reward, iter_no)

        if reward > best_reward:
            print("Best reward updated %.3f -> %.3f" % (best_reward, reward))
            print('=====================================')
            best_reward = reward

        writer.add_scalar("best_reward", best_reward, iter_no)
        if reward > 3.0:
            print('=====================================')
            print("Solved in %d iterations!" % iter_no)
            break

        if iter_no >= 100:
            print('=====================================')
            print("Stopping after 100 iterations!")


        writer.close()
        # tensorboard --logdir runs

    agent.evaluation((50,1,15,0,0,0))
    agent.evaluation((98,3,2,0,0,0))
    agent.evaluation((30,0,10,0,0,0))

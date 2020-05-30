
from env import NFLPlaycallingEnv

def random_play(environment, episodes=1, render=False):

	# for ep in range(episodes):

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

		# print(obs, reward, done)
		if done:
			break

	print("Episode done in {} steps with {:.2f} reward".format(total_steps, total_reward))

if __name__ == '__main__':
	env = NFLPlaycallingEnv()

	random_play(env, render=True)
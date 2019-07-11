from pysc2.env import sc2_env
from pysc2.lib import actions
from utils import arglist

#use agent format from sc2_env
agent_format = sc2_env.AgentInterfaceFormat(
    feature_dimensions=sc2_env.Dimensions(
        screen=(arglist.FEAT2DSIZE, arglist.FEAT2DSIZE),
        minimap=(arglist.FEAT2DSIZE, arglist.FEAT2DSIZE), )
)
"""
minigames
map_name : "DefeatZerglingsAndBanelings", "DefeatRoaches", "CollectMineralShards", "MoveToBeacon", "FindAndDefeatZerglings",b"BuildMarines", "CollectMineralsAndGas"

"""

class MiniGame:
    def __init__(self, map_name, learner, preprocess, nb_episodes=1000):
        #map : "DefeatZerglingsAndBanelings", "DefeatRoaches", "CollectMineralShards", "MoveToBeacon", "FindAndDefeatZerglings",b"BuildMarines", "CollectMineralsAndGas"
        self.map_name = map_name
        #max steps per episodes
        self.nb_max_steps = 2000
        #max episodes
        self.nb_episodes = nb_episodes
        #env from sc2env
        self.env = sc2_env.SC2Env(map_name=self.map_name,
                                  step_mul=16,
                                  visualize=False,
                                  agent_interface_format=[agent_format])
        #algorithm
        self.learner = learner
        #use preprcess functions
        self.preprocess = preprocess

    def run(self, is_training=True):
        #rewards per episodes
        reward_cumulative = []
        for i_episode in range(self.nb_episodes):
            #initialize state from sc2env
            state = self.env.reset()[0]
            for t in range(self.nb_max_steps):  # Don't infinite loop while learning
                #observation from state
                obs = self.preprocess.get_observation(state)
                #selected action(functioncall) from learner to get next state
                actions = self.learner.select_action(obs, valid_actions=obs['nonspatial'])
                #next state
                state = self.env.step(actions=[actions])[0]
                #observation from next state
                obs_new = self.preprocess.get_observation(state)
                #make action stackable form(actions = {'categorical': [], 'screen1': [], 'screen2': []})
                actions = self.preprocess.postprocess_action(actions)
                #stack memory(obs, action, reward, next obs, terminal, training)
                self.learner.memory.append(obs0=obs, action=actions, reward=state.reward,
                                           obs1=obs_new, terminal1=state.last(), training=is_training)

                if state.last():
                    #cum_reward : episode reward
                    cum_reward = state.observation["score_cumulative"]
                    reward_cumulative.append(cum_reward[0])
                    break
            self.learner.optimize(update=True)  # ddpg


        self.env.close()
        print(reward_cumulative)

# Licensing Information:  You are free to use or extend this codebase for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide the following
# attribution:
# This CSCE-689 RL assignment codebase was developed at Texas A&M University.
# The core code base was developed by Guni Sharon (guni@tamu.edu).

from email import policy
import numpy as np
from Solvers.Abstract_Solver import AbstractSolver, Statistics
#env = FrozenLake-v0


class PolicyIteration(AbstractSolver):

    def __init__(self,env,options):
        assert str(env.observation_space).startswith( 'Discrete' ), str(self) + \
                                                                    " cannot handle non-discrete state spaces"
        assert str(env.action_space).startswith('Discrete'), str(self) + " cannot handle non-discrete action spaces"
        super().__init__(env,options)
        self.V = np.zeros(env.nS)
        # Start with a random policy
        self.policy = np.ones([env.nS, env.nA]) / env.nA

    def train_episode(self):
        """
            Run a single Policy iteration. Evaluate and improves the policy.

            Use:
                self.policy: [S, A] shaped matrix representing the policy.
                self.env: OpenAI environment.
                    env.P represents the transition probabilities of the environment.
                    env.P[s][a] is a list of transition tuples (prob, next_state, reward, done).
                    env.nS is a number of states in the environment.
                    env.nA is a number of actions in the environment.
                self.options.gamma: Gamma discount factor.
                np.eye(self.env.nA)[action]
        """

        # Evaluate the current policy
        self.policy_eval()

        # For each state...
        for s in range(self.env.nS):
            # Find the best action by one-step lookahead
            # Ties are resolved arbitarily
            
            ################################
            #   YOUR IMPLEMENTATION HERE   #
            ################################
            q_max = float("-inf")
            best_action = 0
            for action in range(self.env.nA):
                q_value = 0
                for prob, next_state, reward, done in self.env.P[s][action]:
                    q_value += prob * (reward + self.options.gamma * self.V[next_state])
                if q_value > q_max:
                    q_max = q_value
                    best_action = action
            self.policy[s] = np.identity(self.env.nA)[best_action]

        # In DP methods we don't interact with the environment so we will set the reward to be the sum of state values
        # and the number of steps to -1 representing an invalid value
        self.statistics[Statistics.Rewards.value] = np.sum(self.V)
        self.statistics[Statistics.Steps.value] = -1

    def __str__(self):
        return "Policy Iteration"

    def policy_eval(self):
        """····································································```````````````````````````````
        Evaluate a policy given an environment and a full description of the environment's dynamics.
        Use a linear system solver sallied by numpy (np.linalg.solve)

        Use:
            self.policy: [S, A] shaped matrix representing the policy.
            self.env: OpenAI env. env.P represents the transition probabilities of the environment.
                env.P[s][a] is a list of transition tuples (prob, next_state, reward, done).
                env.nS is a number of states in the environment.
                env.nA is a number of actions in the environment.
            theta: We stop evaluation once our value function change is less than theta for all states.
            self.options.gamma: Gamma discount factor.
            np.linalg.solve(a, b) # Won't work with discount factor = 0!
        """
        ################################
        #   YOUR IMPLEMENTATION HERE   #
        ################################
        _V = np.zeros([self.env.nS, self.env.nS])
        target = []
        for s in range(self.env.nS): 
            _V[s][s] = 1 
            sum = 0
            for a, action_prob in enumerate(self.policy[s]):
                for prob, next_state, reward, done in self.env.P[s][a]:
                    _V[s][next_state] = _V[s][next_state] - (self.options.gamma * prob * action_prob)
                    sum = sum + reward*prob*action_prob
            target.append(sum)
        solved_v = np.linalg.solve(_V, target)
        self.V = solved_v


    def create_greedy_policy(self):
        """
        Return the currently known policy.


        Returns:
            A function that takes an observation as input and returns a greedy
            action
        """
        def policy_fn(state):
            q_a = np.zeros(self.env.nA)
            for action in range(self.env.nA):
                for prob, next_state, reward, done in self.env.P[state][action]:
                    q_a[action] += prob * (reward + self.options.gamma * self.V[next_state])
            self.policy[state][np.argmax(q_a)] = 1
            return np.argmax(self.policy[state])

        return policy_fn

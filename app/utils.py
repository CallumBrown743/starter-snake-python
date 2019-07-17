import random
import random
import logging



# credit to https://blog.coast.ai/lets-evolve-a-neural-network-with-a-genetic-algorithm-code-included-8809bece164

class Network():
    """Represent a network and let us operate on it.
    Currently only works for an MLP.
    """

    def __init__(self, nn_param_choices=None):
        """Initialize our network.
        Args:
            nn_param_choices (dict): Parameters for the network, includes:
                nb_neurons (list): [64, 128, 256]
                nb_layers (list): [1, 2, 3, 4]
                activation (list): ['relu', 'elu']
                optimizer (list): ['rmsprop', 'adam']
        """
        self.accuracy = 0.
        self.nn_param_choices = nn_param_choices
        self.network = {}  # (dic): represents MLP network parameters

    def create_random(self):
        """Create a random network."""
        for key in self.nn_param_choices:
            self.network[key] = random.choice(self.nn_param_choices[key])

    def create_set(self, network):
        """Set network properties.
        Args:
            network (dict): The network parameters
        """
        self.network = network

    def print_network(self):
        """Print out a network."""
        logging.info(self.network)
        logging.info("Network accuracy: %.2f%%" % (self.accuracy * 100))


def create_population(self, count):
    """Create a population of random networks.
    Args:
        count (int): Number of networks to generate, aka the
            size of the population
    """
    pop = []
    for _ in range(0, count):
        # Create a random network.
        network = Network(self.nn_param_choices)
        network.create_random()

        # Add the network to our population.
        pop.append(network)

    return pop


def breed(self, mother, father):
    """Make two children as parts of their parents.
    Args:
        mother (dict): Network parameters
        father (dict): Network parameters
    """
    children = []
    for _ in range(2):

        child = {}

        # Loop through the parameters and pick params for the kid.
        for param in self.nn_param_choices:
            child[param] = random.choice(
                [mother.network[param], father.network[param]]
            )

        # Now create a network object.
        network = Network(self.nn_param_choices)
        network.create_set(child)

        children.append(network)

    return children


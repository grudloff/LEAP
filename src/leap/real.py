import random

import numpy as np

from leap.problem import ScalarProblem
from leap.individual import Individual


##############################
# Closure real-genome initializer
##############################
def initialize_vectors(decoder, problem, bounds):
    """

    :param decoder:
    :param problem:
    :param bounds:
    :return:

    >>> from leap import decode, real
    >>> bounds = [(0, 1), (0, 1), (-1, 100)]
    >>> init = initialize_vectors(decode.IdentityDecoder(), real.Spheroid(), bounds)
    >>> for x in init(5):
    ...     print(x) # +doctest: ELLIPSIS
    [...]
    [...]
    [...]
    [...]
    [...]
    """
    def generate_genome():
        for (min, max) in bounds:
            yield random.uniform(min, max)

    def f(pop_size):
        return [Individual(list(generate_genome()), decoder, problem) for _ in range(pop_size)]

    return f


##############################
# Class Spheroid
##############################
class Spheroid(ScalarProblem):
    """ Classic spheroid problem
    """
    def __init__(self, maximize=True):
        super().__init__(maximize)

    def evaluate(self, individual):
        """

        :param individual: to be evaluated
        :return: sum(individual.genome**2)
        """
        return sum([x**2 for x in individual.decode()])


##############################
# Class CosineFamilyProblem
##############################
class CosineFamilyProblem(ScalarProblem):
    def __init__(self, alpha, global_optima_counts, local_optima_counts, maximize=True):
        super().__init__(maximize)
        self.alpha = alpha
        self.dimensions = len(global_optima_counts)
        assert(len(local_optima_counts) == self.dimensions)
        self.global_optima_counts = np.array(global_optima_counts)
        self.local_optima_counts = np.array(local_optima_counts)

    def evaluate(self, phenome):
        phenome = np.array(phenome)
        term1 = -np.cos((self.global_optima_counts - 1) * 2 * np.pi * phenome)
        term2 = - self.alpha * np.cos((self.global_optima_counts - 1) * 2 * np.pi * self.local_optima_counts * phenome)
        value = np.sum(term1 + term2)/(2*self.dimensions)
        # We modify the original function to make it a maximization problem
        # and so that the global optima are scaled to always have a fitness of 1
        return -2/(self.alpha + 1) * value
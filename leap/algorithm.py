from toolz import pipe

from leap import core, util


def simple_ea(generations, pop_size, individual_cls, initialize, decoder, problem, pipeline):
    """
    An example implementation of a basic evolutionary algorithm.

    This function initializes and evaluates a population of size `pop_size`, and then pipes it through an operator
    `pipeline` (i.e. a list of operators) to obtain offspring.  Wash, rinse, repeat.

    The algorithm here is implement at the "metaheuristic" level.  In order to apply it to a particular problem, you
    must provide implementations of its various components: you must decide the population size, how individuals are
    represented and initialized, the pipeline of reproductive operators, etc.

    :param int evals: the stopping condition—stop after `evals` fitness evaluations
    :param int pop_size: Size of the initial population
    :param class individual_cls: class representing the (sub)type of `Individual` the population should be generated
        from
    :param `Decoder` decoder: the Decoder that should be used to convert individual genomes into phenomes
    :param `Problem` problem: the Problem that should be used to evaluate individuals' fitness
    :param evaluate: the evaluation operator
    :param initialize: a function that creates the genomes for the initial population (takes an integer `n` and returns
        a list of `n` genomes
    :param list pipeline: a list of operators that are applied (in order) to the population each generation
    :return: a generator of `(int, individual_cls)` pairs representing the best individual at each generation.

    The intent behind this kind of EA interface is to allow the complete configuration of a basic evolutionary
    algorithm to be defined in a clean and readable way.  If you define most of the components in-line when passing
    them to the named arguments, then the complete configuration of an algorithmic experiment forms one concise code
    block.  Here's what a basic (mu, lambda)-style EA looks like (that is, an EA that throws away the parents at each
    generation in favor of their offspring):

    >>> from leap import core, ops, binary_problems
    >>> l = 10  # The length of the genome
    >>> pop_size = 5
    >>> ea = simple_ea(generations=100, pop_size=pop_size,
    ...                individual_cls=core.Individual, # Use the standard Individual as the prototype for the population
    ...
    ...                decoder=core.IdentityDecoder(),          # Genotype and phenotype are the same for this task
    ...                problem=binary_problems.MaxOnes(),       # Solve a MaxOnes Boolean optimization problem
    ...                initialize=core.create_binary_sequence(length=10),  # Initial genomes are random binary sequences
    ...
    ...                # The operator pipeline
    ...                pipeline=[ops.tournament,                     # Select parents via tournament selection
    ...                          ops.clone,                          # Copy them (just to be safe)
    ...                          ops.mutate_bitflip,                 # Basic mutation: defaults to a 1/L mutation rate
    ...                          ops.uniform_crossover(p_swap=0.4),  # Crossover with a 40% chance of swapping each gene
    ...                          ops.evaluate,                       # Evaluate fitness
    ...                          ops.pool(size=pop_size)             # Collect offspring into a new population
    ...                ])
    >>> ea # doctest:+ELLIPSIS
    <generator ...>

    The algorithm evaluates lazily when you query the generator:

    >>> print(*list(ea), sep='\\n') # doctest:+ELLIPSIS
    (0, Individual(...))
    (1, Individual(...))
    (2, Individual(...))
    ...
    (100, Individual(...))

    In this case, we see that the best individual reported from the initial population (at generation 0),
    followed by the best-so-far individual at each subsequent generation.
    """
    # Initialize a population of pop_size individuals of the same type as individual_cls
    parents = individual_cls.create_population(pop_size, initialize=initialize, decoder=decoder, problem=problem)

    # Evaluate initial population
    parents = core.Individual.evaluate_population(parents)

    # Set up a generation counter that records the current generation to core.context
    generation_counter = util.inc_generation(context=core.context)

    # Output the best individual in the initial population
    bsf = max(parents)
    yield (0, bsf)

    while generation_counter.generation() < generations:
        # Execute the operators to create a new offspring population
        offspring = pipe(parents, *pipeline)

        if max(offspring) > bsf:  # Update the best-so-far individual
            bsf = max(offspring)

        parents = offspring  # Replace parents with offspring
        generation_counter()  # Increment to the next generation

        # Output the best-so-far individual for each generation
        yield (generation_counter.generation(), bsf)
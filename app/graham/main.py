import neural_network
import snake
import threading, queue
import numpy as np
import subprocess
import time
import bottle
import random

sol_per_pop = 50
num_weights = neural_network.num_weights
num_generations = 1000
num_parents_mating = 10

popsize = (sol_per_pop,num_weights)

new_population = np.random.choice(np.arange(-1,1,step=0.01),size=popsize,replace=True)

q = queue.Queue()

max_fitness_idx = 0

#run a game and return the fitness score
def run_game(snake):
	sum = 0
	snake.start()
	for game in range(3):
		response = subprocess.check_output(["engine", "create", "-c", "snake-config.json"])
		subprocess.call(["engine", "run", "-g", str(response)[10:46]])
		sum = sum + q.get()
		print('Game: ',game+1)
	snake.join()
	time.sleep(1)
	return(sum/3)

def get_parents(pop, fitness, num_parents):
	parents = np.empty((num_parents, pop.shape[1]))
	for parent in range(num_parents):
		max_fitness = np.where(fitness==np.max(fitness))
		max_fitness = max_fitness[0][0]
		print(max_fitness)
		parents[parent, :] = pop[max_fitness, :]
		fitness[max_fitness] = -99999999
	return parents

def get_fitness(pop):
	fitness = []
	threads = []
	for i in range(new_population.shape[0]):
		threads.append(threading.Thread(target=snake.run,args=(8080,new_population[i],q,bottle.default_app()),daemon=True))
	for i in range(new_population.shape[0]):
		fit = run_game(threads[i])
		print('fitness value of chromosome '+ str(i) +' :  ', fit)
		fitness.append(fit)
	return np.array(fitness)

def crossover(parents, offspring_size):
    # creating children for next generation 
    offspring = np.empty(offspring_size)
    
    for k in range(offspring_size[0]): 
  
        while True:
            parent1_idx = random.randint(0, parents.shape[0] - 1)
            parent2_idx = random.randint(0, parents.shape[0] - 1)
            # produce offspring from two parents if they are different
            if parent1_idx != parent2_idx:
                for j in range(offspring_size[1]):
                    if random.uniform(0, 1) < 0.5:
                        offspring[k, j] = parents[parent1_idx, j]
                    else:
                        offspring[k, j] = parents[parent2_idx, j]
                break
    return offspring

def mutation(offspring_crossover):
    # mutating the offsprings generated from crossover to maintain variation in the population
    
	for idx in range(offspring_crossover.shape[0]):
		for _ in range(25):
			i = random.randint(0,offspring_crossover.shape[1]-1)
			random_value = np.random.choice(np.arange(-1,1,step=0.001),size=(1),replace=False)
			offspring_crossover[idx, i] = offspring_crossover[idx, i] + random_value

	return offspring_crossover

for generation in range(num_generations):
	fitness = get_fitness(new_population)
	print("Fitness values:")
	print(fitness)
	print('#######  fittest chromosome in generation ' + str(generation) +' is having fitness value:  ', np.max(fitness))
	print('Average fitness: ',np.mean(fitness))
	max_fitness_idx = np.where(fitness == np.amax(fitness))

	parents = get_parents(new_population, fitness, num_parents_mating)
	
	offspring_crossover = crossover(parents, offspring_size=(popsize[0] - parents.shape[0], num_weights))
	
	offspring_mutation = mutation(offspring_crossover)
	
	new_population[0:parents.shape[0], :] = parents
	new_population[parents.shape[0]:, :] = offspring_mutation

print(max_fitness_idx)
max_weights = new_population[max_fitness_idx]
print("I'm done")

while True:
	bestsnake = threading.Thread(target=snake.run,args=(8080,max_weights[0],q,bottle.default_app()),daemon=True)
	bestsnake.start()
	bestsnake.join()
import neural_network
import snake
import threading, queue
import numpy as np
import subprocess
import time
import bottle

sol_per_pop = 10
num_weights = neural_network.num_weights

popsize = (sol_per_pop,num_weights)

new_population = np.random.choice(np.arange(-1,1,step=0.01),size=popsize,replace=True)

fitness = []
threads = []
apps = []

q = queue.Queue()

#run a game and return the fitness score
def run_game(snake):
	snake.start()
	#response = subprocess.check_output(["engine", "create", "-c", "snake-config.json"])
	#subprocess.call(["engine", "run", "-g", str(response)[10:46]])
	snake.join()
	return(q.get())
	
for i in range(new_population.shape[0]):
	threads.append(threading.Thread(target=snake.run,args=(8080,new_population[i],q,bottle.default_app()),daemon=True))
	
	

print(threads)

for i in range(new_population.shape[0]):
	fit = run_game(threads[i])
	print('fitness value of chromosome '+ str(i) +' :  ', fit)
#fit = run_game(threading.Thread(target=snake.run,args=(8080,new_population[1],q)))
#print('fitness value of chromosome '+ str(i) +' :  ', fit)
	fitness.append(fit)
	
print(fitness)

print(123)
import numpy as np

#parameters
inputsize = 8
outputsize = 4
hiddensize1 = 9
hiddensize2 = 15

W1_shape = (hiddensize1,inputsize) #inputs to layer 1
W2_shape = (hiddensize2,hiddensize1) #layer 1 to layer 2
W3_shape = (outputsize,hiddensize2) #layer 2 to outputs

num_weights = inputsize*hiddensize1 + hiddensize1*hiddensize2 + hiddensize2*outputsize
		

def get_weights_from_encoded(individual):
	W1 = individual[0:W1_shape[0] * W1_shape[1]]
	W2 = individual[W1_shape[0] * W1_shape[1]:W2_shape[0] * W2_shape[1] + W1_shape[0] * W1_shape[1]]
	W3 = individual[W2_shape[0] * W2_shape[1] + W1_shape[0] * W1_shape[1]:]
	return (W1.reshape(W1_shape[0], W1_shape[1]), W2.reshape(W2_shape[0], W2_shape[1]), W3.reshape(W3_shape[0], W3_shape[1]))

def softmax(z):
    s = np.exp(z.T) / np.sum(np.exp(z.T), axis=0).reshape(-1, 1)
    return s


def sigmoid(z):
    s = 1 / (1 + np.exp(-z))
    return s
	
def forward_propagation(X, individual):
    W1, W2, W3 = get_weights_from_encoded(individual)

    Z1 = np.matmul(W1, X.T)
    A1 = np.tanh(Z1)
    Z2 = np.matmul(W2, A1)
    A2 = np.tanh(Z2)
    Z3 = np.matmul(W3, A2)
    A3 = softmax(Z3)
    return A3
		
		


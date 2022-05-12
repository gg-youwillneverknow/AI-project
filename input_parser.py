import re, sys
import random
import json 

pattern = r'((?:(?:High|Low);){3}[ENW]);((?:(?:High|Low);){2}(?:High|Low))'
dir = "N"
for i,filename in enumerate(['transition_table.json','policy.json','expected_costs.json']):
	#print(filename)
	file_object = open(filename,'r')
	if i==0:
		transition_table = json.load(file_object)
	if i==1:
		policy = json.load(file_object)
	else:
		expected_costs = json.load(file_object)


def make_transition_table(f):
	
	dict={}
	#do some re and print the output, let's say 5 times

	for i,s in enumerate(list(f.readlines())):
		non_initial = []
		#print(s, end='')
		m = re.search(pattern, s)
		#print(m.group(1) + " " + m.group(2))
		if m.group(1) not in dict:
			dict[m.group(1)] = {m.group(2):1}
			#print(dict)
			#return 0
		else:
			if m.group(2) in dict[m.group(1)]:
				dict[m.group(1)][m.group(2)]+=1
				#print(dict)
				#return 0
			elif m.group(2) not in dict[m.group(1)]:
				dict[m.group(1)][m.group(2)]=1
			
	#print("the number of initial states: ",len(dict))
	l = [len(key) for key in dict]
	#print(l)
	reachable = []
	for key in dict:
		for second_key in dict[key]:
			for i,d in enumerate([";W",';E',";N"]):
				if second_key+d not in dict:
					non_initial += [second_key+d]
			reachable+=[second_key]
	#print(set(reachable))
	#print(set(non_initial))
	#print(dict)
	
	for state in dict: 

		total=sum([dict[state][final_state] for final_state in dict[state]])
		for final_state in dict[state]:
			dict[state][final_state] = dict[state][final_state] / total
	filename = 'transition_table.json'          #use the file extension .json
	with open(filename, 'w') as file_object:  #open the file in write mode
		json.dump(dict, file_object)
	return dict

def main(filename):
	f = open(filename, "r")
	transition_table = make_transition_table(f)
	states = []
	for i,a in enumerate(["High", "Low"]):
		for j,b in enumerate(["High", "Low"]):
			for k,c in enumerate(["High", "Low"]):
				state= a+";"+b+";"+c
				states+=[state]
	expected_costs = {}
	policies = {}
	flag=True
	while(flag):
		flag = False
		for state in states:
			policy,min = value_iteration(state,transition_table,expected_costs)
			if expected_costs.get(state,0)!=min:
				expected_costs[state]=min
				policies[state]=policy
				flag = True
	filename = 'policy.json'          #use the file extension .json
	with open(filename, 'w') as file_object:  #open the file in write mode
		json.dump(policies, file_object)
	
	filename = 'expected_costs.json'          #use the file extension .json
	with open(filename, 'w') as file_object:  #open the file in write mode
		json.dump(expected_costs, file_object)
	pass		


def value_iteration(state,transition_table,expected_costs):
	min = False
	policy = False
	for i,action in enumerate(actions(state)):
		if state == "Low;Low;Low":
			return action,0
		value = cost_function(state,action)
		for final_state in transition_table[state+';'+action]:
			value += transition_table[state+';'+action][final_state]*expected_costs.get(final_state,0)
		
		if bool(min)==False or value<min:
			min = value 
			policy = action 
	return policy,min

def actions(state):
	if state == "Low;Low;Low":
		return next_loop()
	else:
		return ["N","E","W"]

def next_loop():
	global dir
	if dir=="N":
		dir="E"
	elif dir=="E":
		dir="W"
	else:
		dir="N"
	return [dir]

def cost_function(state,action):
	return 1

def show_MDP(transition_table,policy,cost_function):
	MDP={}
	for initial_state in transition_table: 
		states = []
		cost = 0 
		while next_state!='Low;Low;Low':
			action = policy[initial_state]
			cost+=cost_function(initial_state,action)
			n = len(transition_table[initial_state+";"+action])
			next_state = 0
			random_number = random.uniform(0,1)
			for state in transition_table[initial_state]:
				prob = transition_table[initial_state][state]
				if prob >= random_number: 
					next_state = state
				else:
					random_number-= prob
			states.append(next_state)
		MDP[initial_state] = (states,cost)
	return MDP


def true_pdf(x,transition_table,initial_state):
    
	return transition_table[initial_state][x]
	
def true_cdf(x,transition_table,initial_state):
	i = 0 
	global states
	prob = 0
	while states[i]!= x:
		prob += transition_table[initial_state][states[i]] 
	return prob 

if __name__ == "__main__":
	show_MDP(sys.argv[1])

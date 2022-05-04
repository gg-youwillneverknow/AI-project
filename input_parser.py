import re, sys

pattern = r'((?:(?:High|Low);){3}[ENW]);((?:(?:High|Low);){2}(?:High|Low))'

def main(filename):
	f = open(filename, "r")
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
			
	print("the number of initial states: ",len(dict))
	l = [len(key) for key in dict]
	print(l)
	reachable = []
	for key in dict:
		for second_key in dict[key]:
			for i,d in enumerate([";W",';E',";N"]):
				if second_key+d not in dict:
					non_initial += [second_key+d]
			reachable+=[second_key]
	print(set(reachable))
	print(set(non_initial))
	transition_table(dict)
	print(dict)
		
def transition_table(dict):
	
	for state in dict: 

		total=sum([dict[state][final_state] for final_state in dict[state]])
		for final_state in dict[state]:
			dict[state][final_state] = dict[state][final_state] / total
	return dict

def value_iteration(dict):
	

	return dict

def cost_function(state,action):
	return 1
if __name__ == "__main__":
	main(sys.argv[1])

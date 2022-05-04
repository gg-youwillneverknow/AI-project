import re, sys

pattern = r'((?:(?:High|Low);){3}[ENW]);((?:(?:High|Low);){2}(?:High|Low))'

def main(filename):
	f = open(filename, "r")
	#do some re and print the output, let's say 5 times
	for _ in range(5):
		s = f.readline()
		#print(s, end='')
		m = re.search(pattern, s)
		print(m.group(1) + " " + m.group(2))
		
		

if __name__ == "__main__":
	main(sys.argv[1])
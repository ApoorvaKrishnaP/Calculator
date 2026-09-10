print("Apoorva here, trying-GHCP")

terms = 10
first, second = 0, 1
fibonacci_series = []

for _ in range(terms):
	fibonacci_series.append(first)
	first, second = second, first + second

print("Fibonacci series:", *fibonacci_series)
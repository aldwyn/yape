def sift(n):
	sieve = range(2, n+1)

	for x in sieve:
		if x != 'x':
			y = x
			while y < len(sieve):
				if sieve[y] != 'x' and sieve[y] % x == 0:
					sieve[y] = 'x'
				y += 1

	return [e for e in sieve if e != 'x']


if __name__ == '__main__':

	print sift(30)
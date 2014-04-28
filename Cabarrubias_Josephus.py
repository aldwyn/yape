from Cabarrubias_CircularLinkedList import *

class Squad(CircularLinkedList):
	pass

class Soldier(Node):

	def __str__(self):
		return '<Souldier: ' + str(self.data) + '>'


# fundamental function
def josephus(n, k):
	squad = Squad()

	for i in xrange(1, n+1):
		squad.add(Soldier(i))

	ctr = 1
	initial = squad.first
	while squad.length > 1:
		if ctr % k == 0:
			squad.remove(initial.data)
		initial = initial.next
		ctr += 1

	try:
		return squad.get(0).data
	except AttributeError:
		return -1


def getSurvivor(size, steps):
	survivor = josephus(size, steps)

	print 'SOLDIERS: ' + str(size)
	print 'STEPS: ' + str(steps)

	if survivor > 0:
		print 'Soldier ' + str(survivor) + ' survives\n'
	else:
		print 'Invalid params passed\n'


if __name__ == '__main__':

	size = 40
	steps = 7
	getSurvivor(size, steps)

	size = 41
	steps = 3
	getSurvivor(size, steps)

	size = 5
	steps = 2
	getSurvivor(size, steps)

	size = 6
	steps = 3
	getSurvivor(size, steps)

	size = 6
	steps = 2
	getSurvivor(size, steps)

	size = 2
	steps = 1
	getSurvivor(size, steps)

	size = 0
	steps = 0
	getSurvivor(size, steps)

	size = 500
	steps = 3
	getSurvivor(size, steps)

	size = 23
	steps = 3
	getSurvivor(size, steps)

	size = 31
	steps = 4
	getSurvivor(size, steps)

	size = 20
	steps = 5
	getSurvivor(size, steps)

	size = 41
	steps = 3
	getSurvivor(size, steps)

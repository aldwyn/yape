from pprint import pprint

class Vigenere:

	def __init__(self, shift, std_alphabet):
		self.shift = shift
		self.std_alphabet = std_alphabet


	def get_mixed_alphabet(self, keyword):
		non_repeating = ''
		for i in keyword:
			if i not in non_repeating:
				non_repeating += i

		m_alphabet = non_repeating + ''.join([s for s in self.std_alphabet if s not in non_repeating])
		shifted = [m_alphabet[i:i+self.shift] for i in xrange(0, len(m_alphabet), self.shift)]

		mixed = ''
		for j in xrange(len(shifted[0])):
			for i in xrange(len(shifted)):
				try:
					mixed += shifted[i][j]
				except IndexError:
					pass
					
		return mixed


	def get_key(self, password, length):
		return ''.join(password[pointer%len(password)] for pointer in xrange(length))


	def get_vigenere(self, password, m_alphabet):
		return [s+m_alphabet.split(s)[1]+m_alphabet.split(s)[0] for s in m_alphabet]


	def encrypt(self, password, message):
		vigenere = self.get_vigenere(password, self.get_mixed_alphabet(password))
		key = self.get_key(password, len(message))
		cypher = [vigenere[self.std_alphabet.find(key[i])][self.std_alphabet.find(message[i])] for i in xrange(len(message))]
		return ''.join(cypher)


	def decrypt(self, password, cypher):
		vigenere = self.get_vigenere(password, self.get_mixed_alphabet(password))
		key = self.get_key(password, len(cypher))
		crack = [self.std_alphabet[vigenere[self.std_alphabet.find(key[i])].find(cypher[i])] for i in xrange(len(cypher))]
		return ''.join(crack)


if __name__ == '__main__':

	v = Vigenere(5, 'abcdefghijklmnopqrstuvwxyz1234567890 ')

	password = 'excaliburrr'
	message = 'now is the time for all good men to come to the aid of their fellow man'
	cypher = v.encrypt(password, message)
	crack = v.decrypt(password, cypher)
	pprint(v.get_vigenere(password, v.get_mixed_alphabet(password)))

	print 'MESSAGE:\t' + message
	print 'KEY:\t\t' + v.get_key(password, len(message))
	print 'CYPHER:\t\t'+ cypher
	print 'CRACK:\t\t'+ crack

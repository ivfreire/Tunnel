
def sniff(data, source, id):
	try:
		print('{}:\t{}'.format(source, data))
	except Exception as e:
		print(e)
	return data
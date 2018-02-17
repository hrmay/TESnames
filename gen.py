import markovify

def generateName(parameters):
	
	text = "";

	with open("./names/altmer/female.txt") as f:	
	text = f.read()

	text_model = markovify.NewlineText(text, state_size=2);

	for i in range(15):
		name = None
		while name is None:
			name = text_model.make_sentence(tries=100)
		
		print("".join(name.split()))

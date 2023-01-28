from chatgpt_wrapper import ChatGPT
import main,db

chatbot = ChatGPT()

def eulogize(name):
	if db.check_for_character(name) == None:
		response = chatbot.ask(f"Write a funny error message for the text input '{name}'.")
		
	else:
		data = main.fetch_euology_data(name)
		response = chatbot.ask(f"Write a short eulogy for {data['name']}, a {data['race']} {data['spec']} {data['class']}, who resided {data['realm']}.")
	return response

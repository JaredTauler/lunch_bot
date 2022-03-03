import anvil.server

def auth(token):
	anvil.server.connect(token)

def lunch_to_server(user, milk):
	return anvil.server.call('discord_lunch', user, milk)

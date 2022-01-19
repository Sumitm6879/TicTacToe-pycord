import discord
from discord.ext import commands
from discord.ui import View, Button
"""
You can always make it better 😉
"""
class tictactoe(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def ttt(self, ctx, user:discord.Member=None):
		if user is None and ctx.message.reference:
			msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
			user = msg.author
		elif user is None:
			return await ctx.reply("You need to mention a user to play with!")

		player_1 = ctx.author # the one who takes "X"
		player_2 = user  # the one who gets "O"
		view = View(timeout=120)
		view.last_move = str(player_2.id) # I prefer to keep it in string you can make it int also

		for row in range(3):
			for column in range(3):
				view.add_item(Button(row=row,label="\u200b", style=discord.ButtonStyle.grey, custom_id=f'{row} {column}'))
				#                                   ^^ zero-width char
		mesg = await ctx.send("{}'s Turn".format(player_1.mention), view=view) 
		view.turns = 0 # storing the turns to end the game 
		view.board = [
		["-", "-", "-"],
		["-", "-", "-"],
		["-", "-", "-"]
		] # basic board for logic building

		async def button_callback(interaction):
			if interaction.message.id == mesg.id and interaction.user in [player_1, player_2]:
				if view.last_move == f"{interaction.user.id}": # check for last user who played
					await interaction.response.send_message(content="It's not your turn!", ephemeral=True)
					return
				for child in view.children:
					if child.custom_id == interaction.data['custom_id']:
						row = int(child.custom_id[0]) # getting row and col to mark the user's 
						col = int(child.custom_id[2]) # answer on "view.board"
						if interaction.user == player_1:
							child.label = "X" # var for "X" you can even use an emoji
							view.board[row][col] = child.label # marking the response on "view.board"
							child.style = discord.ButtonStyle.red
							next_user = player_2  # storing the next user to mention him in the message

						elif interaction.user == player_2:
							child.label = "O" # var for "O" 
							view.board[row][col] = child.label
							child.style = discord.ButtonStyle.primary
							next_user = player_1
						child.disabled = True # disabling the clicked button 
						
						view.turns += 1 # incrementing the turns count to end at 9
						
						view.last_move = f"{interaction.user.id}" # update the last_move made by member
						await interaction.response.defer() # defrer the response to get clean look 
						await mesg.edit(content=f"{next_user.mention}'s Turn",view=view)
						await check_winner(interaction.user.name, child.label, view.board)
						if view.turns == 9: await end_game() # if turns reach 9 view is stopped and game is considered draw			

		async def end_game(): # when there is a tie  
			disable_all_buttons()
			view.stop()
			await mesg.edit(content="Nobody won!", view=view)

		async def check_winner(user, label, board):
			"""
			The main logic is here this part gets executed
			after every turn to check for the winner
			"""
			if check_rows(label, board):
				await winner(user)

			elif check_cols(label, board):
				await winner(user)

			elif check_diagonal(label, board):
				await winner(user)
			else:
				pass 

		async def winner(user): # the basic call to edit the message according to winner
			disable_all_buttons()
			view.stop()
			await mesg.edit(content="{} won".format(user), view=view)

		def check_rows(label, board): # checks all Rows to get the winner
			for row in board:
				row_is_complete = True
				for slot in row:
					if slot != label:
						row_is_complete = False
						break
				if row_is_complete: return True
			return False

		def check_cols(label, board): # checks all Column to get the winner
			for col in range(3):
				col_is_complete = True
				for row in range(3):
					if board[row][col] != label:
						col_is_complete = False
						break
				if col_is_complete: return True
			return False

		def check_diagonal(label, board): # cheks both diagonal to get winner
			if board[0][0] == label and board[1][1] == label and board[2][2] == label: return True
			elif board[0][2] == label and board[1][1] == label and board[2][0] == label: return True
			else: return False 

		async def button_timeout(): # to end after "120s" of inactivity
			view.stop()
			disable_all_buttons()
			await mesg.edit(content="Timeout! you took too long to play", view=view)

		def disable_all_buttons(): # to disable all buttons 
			for button in view.children:
				button.disabled = True

		for child in view.children: # adding callback to every button added 
			child.callback = button_callback

		view.check_winner = check_winner # define the function to a view var
		view.on_timeout = button_timeout # basic after timeout func. call

def setup(bot):
	"""Add TicTacToe cog to bot"""
	bot.add_cog(tictactoe(bot))

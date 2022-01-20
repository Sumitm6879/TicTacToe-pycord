import discord
from discord.ext import commands
import asyncio
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
			await asyncio.create_task(self.tttai(ctx))
			return 

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

	
	async def tttai(self, ctx):
		"""
        Make and AI play if there is not user to play with 😉
        """
		view= View(timeout=90)
		comp_var = "O"
		user_var = "X"
		view.lastmove = self.bot.user.id
		view.board = {
			1:" ", 2:" ", 3:" ",
			4: " ", 5:" ", 6:" ",
			7:" ", 8:" ", 9:" "}
		cust_id = 1
		for row in range(3):
			for column in range(3):
				view.add_item(Button(row=row,label="\u200b", style=discord.ButtonStyle.grey, custom_id=f"{cust_id}"))
				cust_id +=1
		
		mesg = await ctx.send("{}'s tictactoe".format(ctx.author.mention), view=view)

		async def button_callback(interaction):
			if interaction.message.id == mesg.id and interaction.user == ctx.author:
				if not view.lastmove == ctx.author.id:
					for child in view.children:
						if child.custom_id == interaction.data['custom_id']:
							child.label = user_var
							child.disabled = True 
							child.style = discord.ButtonStyle.danger
							view.board[int(child.custom_id)] = child.label 
							await interaction.response.defer()
							await mesg.edit(view=view)
							await check_winner(interaction.user.name, view.board)
							if check_draw(view.board):
								await mesg.edit(content="Draw! well played! {}".format(interaction.user.name))
								view.stop()
								return
							await compmove(view.board)
		
		def check_draw(board): # checking for draw from the board 
			for key in board.keys():
				if board[key] == " ":
					return False
			return True 
		
		async def check_winner(user, board): # basic win check func. 
			if checkWin(board):
				await winner(user) 
			else:
				pass 

		async def winner(user): # the basic call to edit the message according to winner
			disable_all_buttons()
			view.stop()
			await mesg.edit(content="**{}** WON".format(user), view=view)
		
		def checkWin(board): # check win for user from view button
			if board[1] == board[2] and board[1] == board[3] and board[1] != " ":
				return True
			elif board[4] == board[5] and board[4] == board[6] and board[4] != " ":
				return True
			elif board[7] == board[8] and board[7] == board[9] and board[7] != " ":
				return True

			elif board[1] == board[4] and board[1] == board[7] and board[1] != " ":
				return True
			elif board[2] == board[5] and board[2] == board[8] and board[2] != " ":
				return True
			elif board[3] == board[6] and board[3] == board[9] and board[3] != " ":
				return True

			elif board[1] == board[5] and board[1] == board[9] and board[1] != " ":
				return True
			elif board[3] == board[5] and board[3] == board[7] and board[3] != " ":
				return True

		def checkWinvar(board, var): # a helper function for bot to decide the win 
			if board[1] == board[2] and board[1] == board[3] and board[1] == var:
				return True
			elif board[4] == board[5] and board[4] == board[6] and board[4] == var:
				return True
			elif board[7] == board[8] and board[7] == board[9] and board[7] == var:
				return True

			elif board[1] == board[4] and board[1] == board[7] and board[1] == var:
				return True
			elif board[2] == board[5] and board[2] == board[8] and board[2] == var:
				return True
			elif board[3] == board[6] and board[3] == board[9] and board[3] == var:
				return True

			elif board[1] == board[5] and board[1] == board[9] and board[1] == var:
				return True
			elif board[3] == board[5] and board[3] == board[7] and board[3] == var:
				return True
			else: return False 
		
		def disable_all_buttons(): # to disable all buttons 
			for button in view.children:
				button.disabled = True
		
		async def addcompmove(key): # add the final move decided by bot to message and update it 
			for child in view.children:
				if child.custom_id == str(key) and not child.disabled:
					child.label = comp_var
					child.disabled = True
					child.style = discord.ButtonStyle.primary
					view.board[key] = comp_var
					await mesg.edit(view=view)
					await check_winner(self.bot.user.name, view.board)
				

		async def compmove(board): # getting the move of the bot
			bestmove = 0
			bestscore = -1000
			
			for key in board.keys():
				if board[key] == " ":
					board[key] = comp_var 
					score = minimax(board, 0, False) # run the minimax func. to get the user move which bot simulates himself 
					board[key] = " "
					if score > bestscore:
						bestscore = score
						bestmove = key 
			
			await addcompmove(bestmove)
			return

		def minimax(board, depth, isMaximizing): # minimax logic to get the best move
			if checkWinvar(board, comp_var): # return a high score if bot wins with the move
				return 100
			elif checkWinvar(board, user_var):  # retunr a low score if bot lost
				return -100
			elif check_draw(board): # retunr a newtral score if it's a draw
				return 0
			else: # no need of this block but still i put it
				if isMaximizing: # to check the move of bot 
					bestscore = -1000
					for key in board.keys():
						if board[key] == " ":
							board[key] = comp_var 
							score = minimax(board, 0, False) # rerun the minimax function to get the next user move 
							board[key] = " "
							if score > bestscore:
								bestscore = score
					return bestscore 
				
				else: # to check the move of the user which bot is simulating in order to get best move 
					bestscore = 800
					for key in board.keys():
						if board[key] == " ":
							board[key] = user_var
							score = minimax(board, depth +1, True) # rerun the minimax funtion to get next bot move
							board[key] = " "
							if score < bestscore:
								bestscore = score
					return bestscore  

		async def button_timeout(): # to end after "90s" of inactivity
			view.stop()
			disable_all_buttons()
			await mesg.edit(content="Timeout! you took too long to play", view=view)  
		
		for buttons in view.children:
			buttons.callback = button_callback
		
		view.on_timeout = button_timeout



def setup(bot):
	"""Add TicTacToe cog to bot"""
	bot.add_cog(tictactoe(bot))

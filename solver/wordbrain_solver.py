from __future__ import print_function
from collections import defaultdict
import copy
import sys
import enchant

from .utils import init_grid, read_word_sizes, print_grid, add_word_to_dictionary, get_paths, get_adj, NONECHAR, OVERIDECHAR, REPLACECHAR

class WordbrainSolver:
	def __init__(self, grid_path, personal_word_list_path=None, lang='en_US'):
		self.grid_path = grid_path
		self.personal_word_list_path = personal_word_list_path

		try:
			self.lang_dict = enchant.Dict(lang)
		except:
			sys.exit('the language {} does not exist'.format(lang))

		if personal_word_list_path is not None:
			self.lang_dict = enchant.DictWithPWL(lang, personal_word_list_path)

		self.grid = init_grid(grid_path)
		self.size = len(self.grid) # size of grid (if 4x4, size=4)
		self.num_letters = self.size**2 -  sum([row.count(NONECHAR) for row in self.grid]) # number of letters that we need
		self.word_sizes = read_word_sizes(self.num_letters)

		self.visited = defaultdict(list)
		self.words = defaultdict(list)

		self.words_that_worked = [] # keep track of the words that worked (used in solve())


	def hint(self):
		"""
		Gives the user hints
		if user needs words of length 3, 4, and 5
		It will find all valid words of length 3 and print them
		The user then selects which word it is

		Function removes it from the grid
		Finds all valid words of length 4, etc. until no words left
		"""

		for size_of_word in self.word_sizes[:-1]:
			self.find_words(size_of_word)
			print()

			# possibility that there is nothing in words
			if not len(self.words.keys()):
				sys.exit('no words remaining (could be because the word is not recognized as one (e.g. tv))')

			actual_word = self.words.keys()[0]
			if len(self.words) > 1:
				actual_word = raw_input('What was the word: ')
				if actual_word[0] == OVERIDECHAR:
					# right now, if you go into override block, you're stuck. next chars will all be interpreted as override
					actual_word = actual_word[1:]
					possible_paths = get_paths(actual_word, self.grid)

					while not possible_paths: # this word does not exist
						actual_word = raw_input('Your word is not a valid combination. Please enter another "overide" word: ')
						if actual_word[0] == OVERIDECHAR:
							actual_word = actual_word[1:]

						possible_paths = get_paths(actual_word, self.grid)

					# add the word to the personal word list file
					add_word_to_dictionary(actual_word, self.personal_word_list_path)

					# add word to words dictionary
					self.words[actual_word] = possible_paths

				while actual_word not in self.words:
					actual_word = raw_input('Your word was not in the list: ')

			self.remove_word(actual_word)
			self.reset()

		self.find_words(self.word_sizes[-1]) # take care of the last one
		if not len(self.words):
			print('no words remaining (could be because the word is not recognized as one (e.g. tv))')


	def solve(self):
		"""
		Solves the puzzle completely
		Effectively calls `hint` and tries every word
		Recurses until no words left
		"""

		def solve_completely(word_sizes, ignored_words=None, idx=0):
			assert(ignored_words is None or isinstance(ignored_words, list))

			# if we've gotten this far in the recursive call and there are no more words left to find, we've succeeded
			if not word_sizes:
				return True

			# find all valid words in the grid of length word_sizes[0]
			self.find_words(word_sizes[0], print_words=False)

			# find_words added the words to self.words, so if it is empty, no words were found
			if not self.words:
				return False

			# if there are no more valid words after removing the ones we need to ignore, we have failed
			if not self.words:
				return False

			# make a copy of the valid words and our grid, so we can modify it without losing the original
			our_words = copy.deepcopy(self.words)
			our_grid = copy.deepcopy(self.grid)

			# get our first word and its corresponding path
			cur_word = our_words.keys()[0]
			paths = our_words[cur_word]
			self.words_that_worked.append(cur_word)

			while True:
				# one word may have multiple paths, so we check all of those paths and if they end up not working for us, `paths` will be falsey and 
				# we fetch the next word
				if not paths: # get the next word
					self.words_that_worked.remove(cur_word) # remove the word we were using from our list
					our_words.pop(cur_word) # remove that word from list of valid words
					# if not more valid words left and we still haven't found a solution, we have failed
					if not our_words:
						return False

					cur_word = our_words.keys()[0] # get the new word
					paths = our_words[cur_word]
					self.words_that_worked.append(cur_word)
					continue

				# remove path from actual grid
				self.remove_word_specific_path(paths[0])
				self.reset()

				worked = solve_completely(word_sizes[1:], ignored_words, idx+1)

				if worked:
					# make sure it wasn't one of the ignored word combinations
					if self.words_not_conflicting(ignored_words):
						self.grid = [list(row) for row in our_grid] # reset our grid
						return True
					else:
						# if there was a conflict, we don't need to check the next path, just remove the word entirely
						our_words.pop(cur_word)
						self.words_that_worked.remove(cur_word) # any way thsi could fail? check
						if not our_words:
							return False

						cur_word = our_words.keys()[0] # get the new word
						paths = our_words[cur_word]
						self.words_that_worked.append(cur_word)
						self.grid = [list(row) for row in our_grid] # reset our grid
						self.words = copy.deepcopy(our_words) # reset our words
						continue

				# go to next path
				# remove path from current paths
				paths.pop(0)
				self.grid = [list(row) for row in our_grid] # reset our grid
				self.words = copy.deepcopy(our_words) # reset our words

			return False

		print()

		incorrect_words = [list() for _ in range(len(self.word_sizes))]
		while True:
			solved = solve_completely(self.word_sizes, ignored_words=incorrect_words)
			if not solved:
				print('could not solve')
				break

			for word in self.words_that_worked:
				print(word)
				
			worked = raw_input('Is that correct? ')
			if worked == 'y':
				return

			for i,word in enumerate(self.words_that_worked):
				incorrect_words[i].append(word)

			self.words_that_worked = []


	def words_not_conflicting(self, ignored_words):
		"""
		Return True if the current words_that_worked has not been tried before
		Else return False
		"""

		if len(self.words_that_worked) != len(ignored_words):
			return True

		for pair in zip(*ignored_words):
			for i,word in enumerate(pair):
				if self.words_that_worked[i] != word:
					break
			else: # didn't break, so all words matched/conflicted
				return False

		return True


	def find_words(self, size_of_word, print_words=True):
		"""
		Find all reachable words in the grid
		"""

		for x in range(self.size):
			for y in range(self.size):
				if self.grid[x][y] == NONECHAR:
					continue

				self.find(size_of_word-1, self.grid[x][y], (x,y), ((x,y),), print_words)


	def find(self, currentSize, currentWord, currentIdx, currentPath, print_words):
		"""
		Find valid words and add them to our data structures
		"""

		# if currentSize is 0, our currentWord is the length we want, so simply check if it is a word or not
		if currentSize == 0:
			valid = self.check_if_word(currentWord, print_words)
			if valid:
				self.words[currentWord].append(currentPath)

			return

		# if our word is not the desired length yet, get adjacent, unvisited cells and add each letter to the currentWord
		adjs = get_adj(self.grid, currentIdx, NONECHAR)
		adjs = [adj for adj in adjs if adj not in self.visited[currentPath]] # remove adjacent cells that were already visited

		if not adjs: # no cells left to check
			return

		# loop through univisited cells
		for adj in adjs:
			x,y = adj
			newWord = currentWord + self.grid[x][y]
			newPath = currentPath + (adj,)

	 		# add to visited
			self.visited[currentPath].append(adj)

			# mark everything in currentPath as visited from newPath
			for vertex in currentPath:
				self.visited[newPath].append(vertex)

			self.find(currentSize-1, newWord, adj, newPath, print_words)


	def check_if_word(self, word, print_words):
		"""
		Check if the given 'word' is valid
		"""

		if self.lang_dict.check(word):
			if word not in self.words and print_words:
				print(word)

			return True

		return False
	

	def remove_word(self, word):
		"""
		Remove the given word from the grid by replacing with with NONECHAR and shifting down
		If the word has multiple paths, ask the user which path he/she wants to remove
		"""

		paths = self.words[word]

		# loop through paths and ask which path (if multiple options)
		found = False # True if user said yes to an option
		temp_grid = None
		path = None
		for p in paths[:-1]:
			temp_grid = self.make_temp_grid(p)
			print_grid(temp_grid)

			answer = raw_input('Press "y" if this is the path you used to trace the word: ')
			if answer == 'y':
				path = p
				found = True
				break

		if not found:
			path = paths[-1]

		self.remove_word_specific_path(path)


	def remove_word_specific_path(self, path):
		"""
		Remove path from grid and shift the grid
		"""

		for x,y in path:
			self.grid[x][y] = NONECHAR

		self.shift()


	def make_temp_grid(self, path):
		"""
		Replace a word's characters with REPLACECHAR (given by the path trace)
		"""

		# copy grid
		new_grid = [list(row) for row in self.grid]

		for x,y in path:
			new_grid[x][y] = REPLACECHAR

		return new_grid


	def shift(self):
		"""
		Shift each column down

			e.g.
			a -    =>   - -
			- b    =>   a b
		"""

		for col_idx in range(self.size):
			col = [self.grid[x][col_idx] for x in range(self.size)] # fetch the column
			col = [c for c in col if c != NONECHAR] # remove the NONECHAR
			pad_length = self.size - len(col)

			pad = [NONECHAR]*pad_length
			final_col = pad + col

			self.replace_col(col_idx, final_col)


	def replace_col(self, col_idx, col):
		"""
		Replace the column in the grid (given by 'col_idx') by a new column ('col')
		"""

		for i in range(self.size):
			self.grid[i][col_idx] = col[i]


	def reset(self):
		"""
		Clear 'words' and 'visited' dictionaries
		"""

		self.words = defaultdict(list)
		self.visited = defaultdict(list)

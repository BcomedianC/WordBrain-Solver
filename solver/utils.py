from __future__ import print_function

NONECHAR = '-' # symbol represents empty cell
OVERIDECHAR = '/' # used if correct word is not recognized to be one (e.g. "tv"). user would type "/tv"
REPLACECHAR = '!' # used when printing word paths

def init_grid(grid_path):
	"""
	Initialize the grid by parsing the file given by grid_path
	Grid does not need to be written out as a grid. Can be written
	in any shape (e.g. one line) as long as the number of letters is
	a perfect square

	You can denote spaces in the grid by using the `NONECHAR` character given in wordbrain_solver.py
	"""

	from math import sqrt
	with open(grid_path, 'r') as grid_file:
		grid_str = ''
		for line in grid_file:
			grid_str += line.strip()

	size = int(sqrt(len(grid_str)))
	if len(grid_str) != size**2:
		sys.exit('Grid is not properly shaped')

	#convert the line to a grid (list of lists)
	grid = [grid_str[i:i+size] for i in range(0, size**2, size)]
	return map(list, grid)


def read_word_sizes(num_letters):
	"""
	Read the words sizes from stdin and return a them in a list

	num_letters = grid size^2 - spaces (i.e. the letters left)
	"""

	word_sizes = []

	while num_letters > 0:
		size_of_word = int(raw_input())
		word_sizes.append(size_of_word)
		num_letters -= size_of_word

	return word_sizes


def add_word_to_dictionary(word, personal_word_list_path):
	"""
	Add a word that was not recognized as a valid word to the personal world list,
	so that it will be recognized in the future
	"""

	with open(personal_word_list_path, 'a+') as pwl_file:
		pwl_file.write(word + '\n')


def get_paths(word, grid):
	"""
	Get the list of valid paths of `word` in `grid`
	If no valid paths found, an empty list is returned
	"""

	start_coords = get_coordinates_of_letter(word[0], grid)
	paths = []

	# get  initial paths after having found the first letter
	for coord in start_coords:
		paths.append([coord])

	if len(word) == 1:
		return paths

	# for each letter, look at adjacent letters of the letters which are the last coordinate of paths
	# if they are correct, keep going
	# else remove that path
	for letter in word[1:]:
		path_idx_to_remove = [] # for when we don't find the next letter
		paths_to_add = []
		for i,coords in enumerate(paths):
			found_one = False
			most_recent_coord = coords[-1]
			adjs = get_adj(grid, most_recent_coord, NONECHAR)
			current_path = list(paths[i]) # if I find multiple paths from the same base path, I need to know what it originally was so I can add on to it
			# example: v,x; t,v (word is tv)

			for possible_coord in adjs:
				x,y = possible_coord
				if grid[x][y] == letter:
					if not found_one: # if we haven't found one yet, append to the current path
						paths[i].append(possible_coord)
						found_one = True
					else: # if we already found the next letter, make a copy of the current path and add on the coord
						paths_to_add.append(current_path + [possible_coord])

			if not found_one: # we never found the letter
				path_idx_to_remove.append(i)

		# remove incorrect paths
		paths = [path for i,path in enumerate(paths) if i not in path_idx_to_remove]

		# add new paths
		for path in paths_to_add:
			paths.append(path)

	return paths


def get_coordinates_of_letter(letter, grid):
	"""
	Searches for the letter in the grid and returns a list of all coordinates where it was found
	"""

	coordinates = []

	size = len(grid)
	for x in range(size):
		for y in range(size):
			if grid[x][y] == letter:
				coordinates.append((x,y))

	return coordinates


def valid_path(path):
	"""
	Given a path (iterable of tuples), make sure that they are all different
	"""

	if len(set(path)) == len(path):
		return True

	return False


def get_adj(grid, idx, char_to_ignore):
	"""
	Given a cell (given by 'idx' tuple), return a list of adjacent cells (horizontal, vertical, diagonal)
	"""

	x,y = idx
	adjs = []
	size = len(grid)

	for dx in [-1,0,1]:
		for dy in [-1,0,1]:
			if dx == dy == 0:
				continue

			newX = x + dx
			newY = y + dy

			if newX >=0 and newX < size and newY >= 0 and newY < size:
				if grid[newX][newY] != char_to_ignore:
					adjs.append((newX, newY))

	return adjs


def print_grid(grid):
	"""
	Print the grid in a nice format
	"""

	for row in grid:
		print(' '.join(row))
		
from __future__ import print_function
from subprocess import call
import sys
import os
import webbrowser

try:
	import enchant
except  ImportError:
	print('You need to install the Python module "PyEnchant" to access the dictionary')
	print('Attempting to install "PyEnchant"...')
	try:
		ret_code = call('pip install PyEnchant', shell=True)
		if ret_code < 0:
			print('Child terminated by signal ', -ret_code, file=sys.stderr)
			print('Install "PyEnchant" yourself')
			sys.exit()
	except OSError as e:
		print ('Execution failed: ', e, file=sys.stderr)
		print('Install "PyEnchant" yourself')
		sys.exit()

from solver.wordbrain_solver import WordbrainSolver


CONFIG_DELIM = ':'

def process_lang_input(lang_input, num_languages):
	"""
	Process the user input for choosing a language
	If the input is not an integer, exit
	If it is, make sure it is within the correct bounds

	If so, return True
	else return False
	"""

	try:
		lang_input = int(lang_input)
	except ValueError:
		sys.exit('Input needs to be a number. Exiting.')

	if lang_input >= num_languages or lang_input < 0:
		print('Input needs to be between 0 and {}'.format(num_languages-1))
		return False

	return True


def get_config_params(config_path):
	"""
	Parse the config file and return a dictionary of the params
	For now, the only useful one is "lang"
	Could add the other paths to the config file

	Skip invalid lines
	"""

	config_dict = {}
	with open(config_path) as config_file:
		for line in config_file:
			try:
				key,value = line.split(CONFIG_DELIM)
			except ValueError:
				continue

			config_dict[key] = value

	return config_dict


def write_config_param(config_path, k, new_value):
	"""
	Write they key/value pair to the config file
	If the key already exists, modify the existing value
	"""

	tmp_path = os.path.join(os.path.dirname(config_path), '~' + os.path.basename(config_path))
	with open(config_path, 'r') as config_file, open(tmp_path, 'w') as tmp_file:
		found_key = False

		for line in config_file:
			try:
				key,value = line.split(CONFIG_DELIM)
			except ValueError:
				continue

			if k != key:
				tmp_file.write(line)
			else:
				tmp_file.write('{}{}{}\n'.format(k, CONFIG_DELIM, new_value))
				found_key = True
				break

		# write the rest of the file
		for line in config_file:
			tmp_file.write(line)

		# if key was not found, add it to the end
		if not found_key:
			tmp_file.write('{}{}{}\n'.format(k, CONFIG_DELIM, new_value))

	# delete config file and change tmp_file's name to config_file
	os.remove(config_path)
	os.rename(tmp_path, config_path)


def print_help_message():
	"""
	Print help message describing program functionality
	"""

	msg = """
	python driver.py open: open the grid for editing
	python driver.py hint: displays valid words of given lengths
	python driver.py solve: solves the entire puzzle
	python driver.py languages: let's you choose the language
	python driver.py help: displays this message
	"""

	print(msg)


def main():
	base_path = os.getcwd()
	grid_path = os.path.join(base_path, 'grid.txt')
	pwl_path = os.path.join(base_path, 'personal_word_list.txt')
	config_path = os.path.join(base_path, 'config.txt')

	config_dict = get_config_params(config_path)

	try:
		arg = sys.argv[1]
	except IndexError:
		sys.exit('No action provided: [open, hint, solve]')

	language = 'en_US'
	if 'lang' in config_dict:
		language = config_dict['lang']

	if arg == 'open':
		webbrowser.open(grid_path)

	elif arg == 'hint':
		solver = WordbrainSolver(grid_path, pwl_path, lang=language)
		solver.hint()

	elif arg == 'solve':
		solver = WordbrainSolver(grid_path, pwl_path, lang=language)
		solver.solve()

	elif arg == 'languages':
		available_langs = enchant.list_languages()
		for num,lang in enumerate(available_langs):
			print('{}  {}'.format(num, lang))
		print('Choose a language. Type the number of the language you want.')

		language_num = raw_input()
		while not process_lang_input(language_num, len(available_langs)):
			language_num = raw_input()

		chosen_language = available_langs[int(language_num)]
		write_config_param(config_path, 'lang', chosen_language)

	elif arg == 'help':
		print_help_message()

	else:
		sys.exit('Unrecognized argument: {}'.format(arg))

if __name__ == '__main__':
	main()

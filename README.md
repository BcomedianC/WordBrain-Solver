# WordBrain-Solver
Solves the puzzles in the app WordBrain

You will find three text files:
* config.txt
* personal_word_list.txt
* grid.txt

`config.txt` contains configuration parameters in the format "key:value". As of now, the only one it contains is the `lang` parameter which specifies what language you want to use for the puzzles (the app allows multiple languages).

`personal_word_list.txt` contains words that you want it to recognize as valid words. There are some words (e.g. pulltab) that are not recognized by the dictionary as words. You can modify the file directly, separating the words by a newline, or modify it while running the solver (see below).

`grid.txt` contains the actual grid of the puzzle you are solving. The grid can be of any shape you would like as long as the number of letters is a perfect square.

For example:

Snail level 1 can be inputted as

lse
lid
lod

OR

lselidlod

OR

lseli
dlod

If you want to input partial grid (puzzles that you have partially solved), you can use the hyphen ("-") for the blanks. You will find this character defined in the file `solver/utils.py` with the name `NONECHAR`.

## Using WordBrain Solver

You run `python driver.py` followed by an argument

To see a list of valid arguments, run `python driver.py help`

### Valid arguments:

* help - display valid arguments
* open - opens grid.txt for editing (only tested on Windows; see TODO)
* languages - lets you select the language you want. Constrained by the module `PyEnchant`
* hint - After running the command, type the length of the words you want in the correct order and separated by newlines
  
  The program will print all possible words of a particular length. You will type the word that it is (if the word can be formed using multiple paths, it will display the paths. If the path is right, type 'y'. If it isn't, type anything else or simply press 'Enter'). If the word is not in the list, you can prepend the word using "/" (defined in `solver/utils.py` as `OVERRIDECHAR`) and the word will be automatically added to `personal_word_list.txt`.
* solve - completely solves the puzzle. Like in `python driver.py hint`, input the word lengths and will do the work for you. Some puzzles have multiple possible solutions, but only one works. The program outputs a possible solution. If it works, press 'y', else input any other character or simply press enter. You will not be able to override words when you use the `solve` argument, so they must already be in your personal word list.
 
## TODO

* Multi OS support
  Only tested in Windows. Opening the `.txt` files may lead to problems on OSX/Linux
* Rewrite in C++
  For larger puzzles, the program runs slowly since it needs to bruteforce a solution
* Autopopulate grid using webcam
* When you tell the program that a possible solution is not valid, it does not backtrack, but starts all over. Can be slow. So redesign algorithm.

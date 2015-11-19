## pyhrm
*Tools for analyzing and running Human Resource Machine programs.*

[Human Resource Machine](http://tomorrowcorporation.com/humanresourcemachine)
is a fun little game about programming, so naturally I felt compelled
to write even more (Python) programs to work with my in-game programs.

To export a program from your game,
use the in-game copy button then paste your program into a text editor.
I've started using the file extension `.hrm`, but any plaintext file will do.

###  Usage

All scripts support the `--help` option,
which will display all the optional and required arguments.

**`interpreter.py`**: Runs a program, given the initial memory state and inbox contents.

```bash
# Run the sorter program, with 25 memory cells and a zero in the last cell.
# By default, inbox values are given on stdin, one per line
python interpreter.py --initmem 24 0 --memsize 25 example_programs/sorter.hrm <<EOF
3
7
2
6
0
EOF
2
3
6
7
```

**`extract_images.py`**: Displays the embedded images from a program.

```bash
# Extract images from the sorter program, animating them in a Tk window.
python extract_images.py example_programs/sorter.hrm
```

### Dependencies

 * Python 2.7 or Python 3
 * numpy (for `extract_images.py` only)

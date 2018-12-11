# Librex

This module provides regular expression matching operations similar to those found in Python's re module.

For the regular expression syntax see [Regular Expression Syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax)
and **Known Limitations** section below.

## Installation

Clone Librex source code from GitHub

    # git clone https://github.com/matpuk/testjb.git

Change your current work directory to Librex root

    # cd testjb

Install Librex

    NOTE: Librex requires Python version 3.7 or later

    # python setup.py install

You are now ready to use Librex in your code or do some quick pattern matching using provided cli tool.
See next section for more details.

## Usage

### Public API

Just import the module into your code and start using it

    import librex

    print(librex.match("cat", "dog"))


#### Module Contents

The module defines several functions and an exception.
Some of the functions are simplified versions of the full featured methods for compiled regular expressions.
Most non-trivial applications always use the compiled form.

librex.**compile**(*pattern*)

> Compile a regular expression pattern into a `regular expression object`,
 which can be used for matching using its `match()` method described below.
>
> The sequence
>
>     rex = librex.compile(pattern)
>     result = rex.match(string)
> is equivalent to
>
>     result = librex.match(pattern, string)
>
> but using `librex.compile()` and saving the resulting `regular expression object` for reuse
 is more efficient when the expression will be used several times in a single program.

librex.**match**(*pattern*, *string*)

> If the whole *string* match the regular expression *pattern*, return True. Return False otherwise.

*exception* librex.**RexError**()

> Exception raised when a string passed to one of the Librex functions is not a valid regular expression
 (for example, it might contain unmatched parentheses) or when some other error occurs during compilation.

#### Regular Expression Objects

Compiled regular expression objects support the following methods and attributes:

RexPattern.**match**(*string*)

> If the whole *string* match the regular expression *pattern*, return True. Return False otherwise.
>
>     >>> pattern = librex.compile("cat")
>     >>> pattern.match("dog")
>     False
>     >>> pattern.match("cat")
>     True

RexPattern.**pattern**

> Original pattern string used to build the object

### Command Line Interface

Librex provides cli tool named 're-match' to quickly perform some pattern matching without writing any code.

Usage

    # re-match -h
    usage: re-match [-h] PATTERN STRING

    Apply regular expression PATTERN to string STRING.

    positional arguments:
      PATTERN     regular expression
      STRING      string to apply regular expression PATTERN to

    optional arguments:
      -h, --help  show this help message and exit

    Exit status is 0 if the string STRING matches the regular expression PATTERN,
    1 otherwise; if any error occurs the exit status is 2.

Example

    # re-match "abc|def" "abcd"
    # echo $?
    1

## Developing Librex

In order to contribute to the Librex, you need to install necessary Python modules first

    # pip install -r requirements_devel.txt

And then

    # pip install -e .

You are ready to start playing with the code now.

In order to check that your changes didn't break anything, you can run Librex unit tests

    # python setup.py test

Along with the tests result, code coverage report will be created under the 'htmlcov' folder.
Make sure that your changes do not decrease current code coverage percentage.
Cover your changes with additional unit tests if necessary. Librex uses pytest for this.

Create pull request on GitHub when you are ready and wait for approval.

## Known Limitations

Librex implements only limited subset of regular expressions syntax.

Here are current known limitations of the module (comparing to Python's re module):

- Whole input string is matched. As a result, symbols '^' and '$' are just regular ones.
- The '\*', '+' and '?' qualifiers are all *greedy*; they match as much text as possible.
  There are no *non-greedy* versions of them in Librex. Attempt to use '*?', '+?' or '??'
  qualifiers will lead to `RexError` exception.
- Specifying exact number of matches is not supported. As a result, '{m}', '{m,n}' and '{m,n}?'
  special qualifiers are meaningless and treated as regular symbol sequences.
- Specifying custom symbols set is not supported. Thus, '\[' and ']' are just regular symbols too.
- Extended notations '(?...)' are not supported at all.
- The next special sequences are not supported (`RexError` exception will be thrown):
  '\number', '\A', '\b', '\B', '\Z'

Actual supported regular expressions feature set can be obtained from the librex module at any time

    >>> import librex
    >>> help(librex)

## License

MIT (See 'LICENSE' file for exact license text).

## Author

Grigory V. Kareev

Email: <grigory.kareev@gmail.com>

GitHub: [https://github.com/matpuk](https://github.com/matpuk)

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

import re
from typing import Union
from .ast import is_boolean, is_list
from .types import DiyLangError, String # pylint: disable=unused-import

"""
This is the parser module, with the `parse` function which you'll implement as
part 1 of the workshop. Its job is to convert strings into data structures that
the evaluator can understand.
"""

def try_parse_int(int_string: str) -> Union[int, None]:
    try:
        return int(int_string)
    except ValueError:
        return None

def parse(source: str):
    """Parse string representation of one *single* expression
    into the corresponding Abstract Syntax Tree."""
    # pylint: disable=too-many-return-statements
    if not source:
        return None
    tok1 = remove_comments(source).strip()
    if not tok1:
        return None
    if tok1 == "#t":
        return True
    if tok1 == "#f":
        return False
    tok_as_int = try_parse_int(tok1)
    if tok_as_int is not None:
        return tok_as_int
    if tok1[0] == '(':
        close_paren = find_matching_paren(tok1)
        inner_ast = split_exps(tok1[1:close_paren])
        if tok1[close_paren + 1:]:
            raise DiyLangError("Expected EOF")
        return [parse(inner_tok) for inner_tok in inner_ast]
    if tok1[0] == '\'':
        return ["quote", parse(tok1[1:])]
    return tok1

#
# Below are a few useful utility functions. These should come in handy when
# implementing `parse`. We don't want to spend the day implementing parenthesis
# counting, after all.
#


def remove_comments(source):
    """Remove from a string anything in between a ; and a line break"""
    return re.sub(r";.*\n", "\n", source)


def find_matching_paren(source, start=0):
    """Given a string and the index of an opening parenthesis, determines
    the index of the matching closing paren."""

    assert source[start] == '('
    pos = start
    open_brackets = 1
    while open_brackets > 0:
        pos += 1
        if len(source) == pos:
            raise DiyLangError("Incomplete expression: %s" % source[start:])
        if source[pos] == '(':
            open_brackets += 1
        if source[pos] == ')':
            open_brackets -= 1
    return pos


def split_exps(source):
    """Splits a source string into sub expressions
    that can be parsed individually.

    Example:

        > split_exps("foo bar (baz 123)")
        ["foo", "bar", "(baz 123)"]
    """

    rest = source.strip()
    exps = []
    while rest:
        exp, rest = first_expression(rest)
        exps.append(exp)
    return exps


def first_expression(source):
    """Split string into (exp, rest) where exp is the
    first expression in the string and rest is the
    rest of the string after this expression."""

    source = source.strip()

    if source[0] == "'":
        exp, rest = first_expression(source[1:])
        return source[0] + exp, rest
    if source[0] == "(":
        last = find_matching_paren(source)
        return source[:last + 1], source[last + 1:]

    match = re.match(r"^[^\s)(']+", source)
    end = match.end()
    atom = source[:end]
    return atom, source[end:]

#
# The functions below, `parse_multiple` and `unparse` are implemented in order
# for the REPL to work. Don't worry about them when implementing the language.
#


def parse_multiple(source):
    """Creates a list of ASTs from program source constituting
    multiple expressions.

    Example:

        > parse_multiple("(foo bar) (baz 1 2 3)")
        [['foo', 'bar'], ['baz', 1, 2, 3]]

    """

    source = remove_comments(source)
    return [parse(exp) for exp in split_exps(source)]


def unparse(ast):
    """Turns an AST back into DIY Lang program source"""

    if is_boolean(ast):
        return "#t" if ast else "#f"
    if is_list(ast):
        if ast and ast[0] == "quote":
            return "'%s" % unparse(ast[1])
        return "(%s)" % " ".join([unparse(x) for x in ast])

    # integers or symbols (or lambdas)
    return str(ast)

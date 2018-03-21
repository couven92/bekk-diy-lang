# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,unused-import

import operator
from .types import Environment, DiyLangError, Closure, String
from .ast import is_boolean, is_atom, is_symbol, is_list, is_closure, \
    is_integer, is_string
from .parser import unparse

"""
This is the Evaluator module. The `evaluate` function below is the heart
of your language, and the focus for most of parts 2 through 6.

A score of useful functions is provided for you, as per the above imports,
making your work a bit easier. (We're supposed to get through this thing
in a day, after all.)
"""


def evaluate(ast, env: Environment):
    """Evaluate an Abstract Syntax Tree in the specified environment."""
    if is_list(ast) and ast:
        if is_closure(ast[0]):
            closure = ast[0] # type: Closure
            inner_env = closure.env.extend(dict(zip(closure.params, \
                [evaluate(v, env) for v in ast[1:]])))
            # inner_env = Environment(dict(zip(closure.params, \
            #     [evaluate(v, env) for v in ast[1:]])))
            return evaluate(closure.body, inner_env)
        if ast[0] == "quote":
            return ast[1]
        if ast[0] == "atom":
            return is_atom(evaluate(ast[1], env))
        if ast[0] == "define":
            if len(ast) != 3:
                raise DiyLangError("Wrong number of arguments. " \
                    "Got {}, expected {}".format(len(ast) - 1, 2))
            symbol = ast[1]
            if not is_symbol(symbol):
                raise DiyLangError("{} is not a symbol.".format(symbol))
            env.set(symbol, evaluate(ast[2], env))
            return None
        if ast[0] == "lambda":
            if len(ast) != 3:
                raise DiyLangError("Wrong number of arguments. " \
                    "Got {}, expected {}".format(len(ast) - 1, 2))
            arg1 = ast[1]
            if not is_list(arg1):
                raise DiyLangError("Argument 1 to 'lambda' must be a list")
            arg2 = ast[2]
            return Closure(env, arg1, arg2)
        left = evaluate(ast[1], env)
        right = evaluate(ast[2], env)
        if ast[0] == "eq":
            return is_atom(left) and is_atom(right) and left == right
        operator_dict = {
            '+': operator.add,
            '-': operator.sub,
            '/': operator.floordiv,
            '*': operator.mul,
            "mod": operator.mod,
            '<': operator.lt,
            '>': operator.gt
        }
        opcode = operator_dict.get(ast[0])
        if opcode is not None:
            if not is_integer(left):
                raise DiyLangError()
            if not is_integer(right):
                raise DiyLangError()
            return opcode(left, right)
        if ast[0] == "if":
            cond = left
            left = right
            right = evaluate(ast[3], env)
            if not is_boolean(cond):
                raise DiyLangError()
            return left if cond else right
    if is_symbol(ast):
        var = env.lookup(ast)
        if is_closure(var):
            return evaluate([var, *ast[1:]], env)
        return var
    return ast

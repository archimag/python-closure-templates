# -*- coding: utf-8 -*-
# 
# Copyright 2012 Moskvitin Andrey <archimag@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.  You
# may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.


from lepl import *

def namedFields(**attrIndexMap):
    def __getattr__(self, name):
        if name in attrIndexMap:
            return self[attrIndexMap[name]]
        else:
            raise AttributeError(name)

    def impl(origin_class):
        origin_class.__getattr__ = __getattr__
        return origin_class

    return impl


def toPrefixExpression(expr):
    prefix = toPrefix(expr)

    if len(prefix) == 1:
        return prefix[0]
    else:
        return Expression(prefix)


class Expression(List): pass

expression = Delayed()

# whitespace

iW = Drop(Any(' \t\n\r')[1:])
oW = Drop(Any(' \t\n\r')[0:])

# string literal

def escapeSequence(arg, value=None):
    return Substitute(Literal("\\%s" % arg), value or arg)

reverseSolidus = escapeSequence('\\')
apostrophe = escapeSequence("'")
quotationMark = escapeSequence('"')
newLine = escapeSequence('n', '\n')
carriageReturn = escapeSequence('r', '\r')
tab = escapeSequence('t', '\t')
backspace = escapeSequence('b', '\b')
formFeed = escapeSequence('f', '\f')

hexChar = Any('0123456789ABCDEFabcdef')

stringChar = Or(reverseSolidus,
                apostrophe,
                quotationMark,
                newLine,
                carriageReturn,
                tab,
                backspace,
                formFeed,
                AnyBut("'"))

string = Drop("'") + stringChar[0:] + Drop("'")

# number literal

def parseDecimalInteger(args):
    return [int("".join(args))]

def parseHexadecimalInteger(args):
    return [int("".join(args), 16)]

def parseFloat(args):
    return [float("".join(args))]

decimalInteger = Digit()[1:] >= parseDecimalInteger

hexadecimalInteger = ~Literal('0x') & hexChar[1:] >= parseHexadecimalInteger

integer = hexadecimalInteger | decimalInteger

floatNumber = Digit()[1:] & '.' & Digit()[0:] & Optional(Any('Ee') & Optional(Any('+-')) & Digit()[0:] ) >= parseFloat

number = floatNumber | integer 

# null and boolean literal

null = Substitute("null", None)
true = Substitute("true", True)
false = Substitute("false", False)
boolean = true | false

# literal

expressionLiteral = number | null | boolean | string

# variable

alphanumeric = Letter() | Digit()
simpleName = Letter() + Or(alphanumeric, '_')[0:]

class Ref(List): pass

@namedFields(name=0, expr=1)
class DotRef(Ref): pass
dotRef = (Drop('.') & simpleName) | (Drop('[') & simpleName & Drop(']'))  > DotRef

@namedFields(position=0, expr=1)
class ARef(Ref): pass
aRef = (Drop('[') & expression & Drop(']')) | (Drop('.') & integer) > ARef

@namedFields(name=0)
class Variable(List): pass

variable = Drop('$') & simpleName > Variable

# funcall

@namedFields(name=0, args=slice(1, None))
class Funcall(List): pass

funcall = (simpleName
           & oW
           & ~Literal('(')
           & oW
           & Optional(expression & (oW  & ~Literal(',') & oW & expression)[0:])
           & oW
           & ~Literal(')')) > Funcall


# operator
@namedFields(op=0, args=slice(1, None))
class Operator(List): pass

operator = Or('-', 'not', '*', '/', '%', '+', '<=', '>=', '<', '>', '==', '!=', 'and', 'or', '?', ':') > Operator

# parenthesis

parenthesis = Drop('(') & oW & expression & oW & Drop(')') > toPrefixExpression    

# expression

def reduceRef(expr):
    while len(expr) > 1:
        for pos, item in enumerate(expr):
            if isinstance(item, Ref) and len(item) == 1:
                item.append(expr[pos-1])
                expr[pos-1:pos+1] = [item]
                break
        
    return expr

expressionPart = (expressionLiteral | variable | funcall | parenthesis) & ((dotRef | aRef)[0:]) >= reduceRef

def reduceInfix(infix):
    def isOperator(obj, optype):
        return isinstance(obj, Operator) and obj[0] == optype
    
    # - (unary)
    if isOperator(infix[0], '-') and not infix[0].args:
        infix[0].append(infix[1])
        infix[0:2] = [Operator(['neg', infix[1]])]
        return

    # ?: ternary
    for pos1, item1 in enumerate(infix):
        if isOperator(item1, '?'):
            for pos2, item2 in enumerate(infix[pos1+1:], pos1 + 1):
                if isOperator(item2, ':'):
                    infix[:] = [Operator(['if',
                                          toPrefixExpression(infix[0:pos1]),
                                          toPrefixExpression(infix[pos1+1:pos2]),
                                          toPrefixExpression(infix[pos2+1:])])]
                    return

            raise Exception(": not found")


    # binary operators
    for ops in [['not'], ['*', '/', '%'], ['+', '-'], ['<', '>', '<=', '>='], ['==', '!='], ['and'], ['or']]:
        for pos, item in enumerate(infix):
            if isinstance(item, Operator) and (len(item.args) == 0) and (item.op in ops):
                if item.op == 'not':
                    item.append(infix[pos+1])
                    infix[pos:pos+2] = [item]
                    return
                else:
                    item.append(infix[pos-1])
                    item.append(infix[pos+1])
                    infix[pos-1:pos+2] = [item]
                    return

def toPrefix(expr):
    while len(expr) > 1:
        reduceInfix(expr)

    return expr

expression += (oW
               & Optional((Literal('-') > Operator) | (Literal('not') > Operator))
               & oW
               & expressionPart
               & (oW & operator & oW & expressionPart)[0:]
               & oW) > toPrefixExpression
    

def parseExpression(text):
    return expression.parse(text)[0]

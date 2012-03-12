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

import re
from lepl import *
from expression import namedFields, simpleName, expressionLiteral, expression, variable, boolean, iW, oW
import codecs

def isText(text):
    return isinstance(text, str) or isinstance(text, unicode)

class CodeBlock(List): pass
codeBlock = Delayed()

# comment

class Comment(List): pass

class SimpleComment(Comment): pass
simpleComment = Drop("//") + (~Lookahead('\n') + Any())[0:] > SimpleComment

class MultilineComment(Comment): pass
multilineComment = Drop('/*') + (~Lookahead('*/') + Any())[0:] + Drop('*/') > MultilineComment

comment = simpleComment | multilineComment

# simple text

def simpleTextHandler(args):
    return re.sub('\\s+', ' ', args[0])

simpleText =  Add(Or(Drop(iW & comment), AnyBut("{}"))[1:]) > simpleTextHandler

# substition

@namedFields(char=0)
class Substition(List): pass

substition = Or(Substitute('{sp}', Substition([' '])),
                Substitute('{nil}', Substition([''])),
                Substitute('{\\r}', Substition(['\r'])),
                Substitute('{\\n}', Substition(['\n'])),
                Substitute('{\\t}', Substition(['\t'])),
                Substitute('{lb}', Substition(['{'])),
                Substitute('{rb}', Substition(['}'])))

# literal

@namedFields(text=0)
class LiteralTag(List): pass

literal = Drop("{literal}") + (~Lookahead('{/literal}') + Any())[0:] + Drop('{/literal}') > LiteralTag

# print

@namedFields(expr=0, directives=1)
class Print(List): pass

def printHandler(args):
    directives = dict()

    for item in args[1:]:
        if isinstance(item, tuple):
            directives[item[0]] = item[1]
        else:
            directives[item] = True

    args[1:] = [directives]

    return Print(args)

printDirective = Drop("|") & oW & Or(simpleName, simpleName & Drop(':') & expressionLiteral > tuple)
printTag = Drop(Or("{print ", "{")) &oW & expression & (printDirective | iW)[0:] & Drop("}") > printHandler

# if
class If(List): pass

def elseIfHandler(args):
    if len(args) > 1:
        return (args[0], args[1])
    else:
        return (True, args[0])

_else = Drop('{else}') & codeBlock > elseIfHandler
_elseIf = Drop('{elseif') & iW & expression & oW & Drop('}') & codeBlock > elseIfHandler
_if = (Drop('{if')
       & iW
       & (expression & oW & Drop('}') & codeBlock > elseIfHandler)
       & _elseIf[0:]
       & Optional(_else)
       & Drop('{/if}')) > If


# switch

@namedFields(expr=0, cases=slice(1, None))
class Switch(List): pass

def caseHandler(args):
    return (args[0:-1], args[len(args) - 1])

_case = (Drop('{case')
         & iW
         & expressionLiteral
         & (~Lookahead('}') & oW & Drop(',') & oW & expressionLiteral)[0:]
         & oW
         & Drop('}') & codeBlock > caseHandler)
_default = Drop('{default}') & codeBlock
_switch = (Drop('{switch')
           & iW
           & expression
           & oW
           & Drop('}')
           & (iW | _case)[0:]
           & Optional(_default)
           & Drop('{/switch}')) > Switch

# foreach

@namedFields(var=0, expr=1, code=2, ifEmptyCode=3)
class Foreach(List): pass

def foreachHandler(args):
    foreach_ = Foreach(args)

    if len(foreach_) < 4:
        foreach_.append(None)

    return foreach_

_ifempty = Drop('{ifempty}') & codeBlock
_foreach = (Drop('{foreach')
            & iW
            & variable
            & iW
            & Drop('in') & iW & expression & oW & Drop('}')
            & codeBlock
            & Optional(_ifempty)
            & Drop('{/foreach}')) > foreachHandler

# for

@namedFields(var=0, range=slice(1, -1), code=-1)
class For(List): pass

_range = Drop('range(') & oW & expression & (oW & Drop(',') & expression)[0:2] & oW & Drop(')')
_for = Drop('{for') & iW & variable & iW & Drop('in') & iW & _range &oW & Drop('}') & codeBlock & Drop('{/for}') > For

# call

@namedFields(name=0, data=1, params=slice(2, None))
class Call(List): pass

def callHandler(args):
    if len(args) == 1:
        args.append(None)
    elif isinstance(args[1], tuple):
        args.insert(1, None)
        
    return Call(args)

_param = (Drop('{param') & iW & simpleName &
          Or(oW  & Drop(':') & oW  & expression & oW & Drop('/}'),
             Drop('}') & codeBlock & Drop('{/param}'))) > tuple

_callData = Substitute('data="all"', True) | (Drop('data="') & expression & Drop('"'))
_callTemplateName = simpleName | (Drop('name=\"') & expression & Drop('\"'))
_call = (Drop('{call')
         & iW
         & _callTemplateName
         & Optional(iW & _callData)
         & oW
         & Or(Drop('/}'),
              Drop('}') & (_param | iW)[0:] & Drop('{/call}'))) > callHandler

# codeBlock

class CodeBlock(List): pass

def codeBlockHandler(args):
    if args and isText(args[0]):
        args[0] = args[0].lstrip()

    if args and isText(args[-1]):
        args[-1] = args[-1].rstrip()

    for i in xrange(len(args)):
        if isinstance(args[i], Substition):
            if i > 0 and isText(args[i-1]):
                args[i-1] = args[i-1].rstrip()

            if i < (len(args) - 1) and isText(args[i+1]):
                args[i+1] = args[i+1].lstrip()

    return CodeBlock(filter(None, args))

codeBlock += Or(comment,
                simpleText,                
                literal,
                _call,
                _if,
                _foreach,
                _switch,
                _for,
                substition,
                #with,                
                printTag,
                )[0:] > codeBlockHandler

# template

@namedFields(name=0, props=1, code=2)
class Template(List): pass

def templateHandler(args):
    props = dict()

    for (key, value) in args[1:-1]:
        props[key] = value

    args[1:-1] = [props]

    return Template(args)

templateStart = (Drop('{template') & iW & simpleName
                 & Optional(iW & Drop('') & 'autoescape' & Drop('=') & Drop('"') & boolean & Drop('"') > tuple)
                 & Optional(iW & Drop('') & 'private' & Drop('="') & boolean & Drop('"') > tuple)
                 & oW
                 & Drop('}'))
templateEnd = Drop('{/template}')
template = templateStart & codeBlock & templateEnd > templateHandler

def parseSingleTemplate(text):
    return template.parse(text)[0]

# namespace

@namedFields(name=0, templates=slice(1, None))
class Namespace(List): pass

namespace = (Drop((comment | iW)[0:])
             & Drop('{namespace') & iW & (simpleName + (Literal('.') + simpleName)[0:]) & oW & Drop('}')
             & (Drop(comment) | template | iW)[0:])> Namespace

matcher = namespace
matcher.config.clear()

def parseNamespace(text):
    return matcher.parse(text)[0]

def parseFile(path):
    with codecs.open(path, encoding='utf-8') as f:
        return parseNamespace(f.read())

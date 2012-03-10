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

import operator
import math
from random import randint
from numbers import Number
from StringIO import StringIO
from contextlib import closing

from parser import *

####################################################################################################
# ttable
####################################################################################################

class TTable(object):
    def __init__(self, prototype=None):
        self.dict = dict()
        self.prototype = prototype

    def clear(self):
        self.dict.clear()

    def findTemplate(self, name):
        if name in self.dict:
            return self.dict.get(name)
        elif self.prototype:
            return self.prototype.findTemplate(name)
        else:
            return None

    def registerTempalte(self, name, template, supersede=False):
        if (not supersede) and (name in self.dict):
            raise Exception('Template %s has already been registered' % name)
        
        self.dict[name] = template

    def callTemplate(self, name, env, out=None):
        if out:
            template = self.findTemplate(name)
            if not template:
                raise Exception('Template %s is undefined' % name)
            template(env, out, ttable=self)
        else:
            with closing(StringIO()) as out:
                self.callTemplate(name, env, out=out)
                return out.getvalue()

    def templateNameList(self):
        names = self.dict.keys()
        
        if self.prototype:
            names.extend(self.prototype.templateNameList)

        names.sort()
        return names

####################################################################################################
# environment
####################################################################################################

class Env(object):
    def __init__(self, base, extra):
        self.base = base
        self.extra = extra

    def __str__(self):
        return "<Env %s, %s>" % (str(self.base), str(self.extra))

####################################################################################################
# escape
####################################################################################################

def escapeHtml(text):
    out = StringIO()

    for ch in text:
        if ch == '<':
            out.write('&lt;')
        elif ch == '>':
            out.write('&gt;')
        elif ch == '"':
            out.write('&quot;')
        elif ch =="'":
            out.write('&#039;')
        elif ch == '&':
            out.write('&amp;')
        else:
            out.write(ch)

    return out.getvalue()

def encodeString(text, notEncode):
    out = StringIO()

    for ch in text:
        if (chr(0) <= ch <= chr(9)) or ('a' <= ch <= 'z') or ('A' <= ch <= 'Z') or (ch in notEncode):
            out.write(str(ch))
        else:
            for octet in ch.encode('utf-8'):
                out.write('%%%02X' % ord(octet))

    return out.getvalue()

def encodeUri(text):
    return encodeString(text, '~!@#$&*()=:/,;?+\'')

def encodeUriComponent(text):
    return encodeString(text, '~!*()\'')
    
    
####################################################################################################
# expression handler
####################################################################################################

def fetchProperty(obj, key):
    if isinstance(obj, dict):
        return obj.get(key)
    if isinstance(obj, Env):
        ex = fetchProperty(obj.extra, key)
        if ex != None:
            return ex
        else:
            return fetchProperty(obj.base, key)
    else:
        return getattr(obj, key)

def makeConstantlyHandler(value):
    def constantlyHandler(env):
        return value
    
    return constantlyHandler

def makeDotRefHandler(expr, key):
    def dotHandler(env):
        return fetchProperty(expr(env), key(env))

    return dotHandler

def makeARefHandler(expr, pos):
    def aRefHandler(env):
        return expr(env)[pos(env)]
    return aRefHandler

def makeVariableHandler(var):
    def variableHandler(env):
        return fetchProperty(env, var)

    return variableHandler

def genericAdd(arg1, arg2):
    if isinstance(arg1, Number) and isinstance(arg2, Number):
        return arg1 + arg2
    else:
        return str(arg1) + str(arg2)

def makeOperatorHandler(name, args):
    if len(args) == 1:
        unaryOps = { 'neg': operator.neg,
                     'not': operator.not_ }

        arg = args[0]
        op = unaryOps[name]

        if not op:
            raise Exception("Unknow unary operator: %s" % name)

        def unaryOperatorHandler(env):
            return op(arg(env))

        return unaryOperatorHandler
    elif len(args) == 2:
        binaryOps = { '-': operator.sub,
                      '*': operator.mul,
                      '/': operator.truediv,
                      '%': operator.mod,
                      '+': genericAdd,
                      '<=': operator.le,
                      '>=': operator.ge,
                      '<': operator.lt,
                      '>': operator.gt,
                      '==': operator.eq,
                      '!=': operator.ne }
        
        a = args[0]
        b = args[1]
        op = binaryOps.get(name)

        if op:
            def binaryOperatorHandler(env):
                return op(a(env), b(env))
            return binaryOperatorHandler
        elif name == 'and':
            def andOperatorHandler(env):
                return a(env) and b(env)
            return andOperatorHandler
        elif name == 'or':
            def orOperatorHandler(env):
                return a(env) or b(env)
            return orOperatorHandler                
        else:
            raise Exception('Unknow binary operator: %s' % name)
    elif len(args) == 3:
        if name == 'if':
            cond = args[0]
            then_ = args[1]
            else_ = args[2]
            
            def ifOperatorHandler(env):
                if cond(env):
                    return then_(env)
                else:
                    return else_(env)

            return ifOperatorHandler
        else:
            raise Exception('Unknow ternary operator: %s' % name)
    else:
        raise Exception('Bad operator arguments')

def ctRound(number, ndigits=None):
    if ndigits:
        return round(number, ndigits)
    else:
        return int(round(number))

def loopVariableCounterName(varName):
    return '%%counter_%s' % varName

def loopSequenceName(varName):
    return '%%sequence_%s' % varName

def makeLoopIndex(varName):
    counterName = loopVariableCounterName(varName)
    
    def loopIndex(env):
        return fetchProperty(env.extra, counterName) + 1

    return loopIndex

def makeLoopIsFirst(varName):
    counterName = loopVariableCounterName(varName)
    
    def loopIsFirst(env):
        return (0 == fetchProperty(env, counterName))
    
    return loopIsFirst

def makeLoopIsLast(varName):
    seqName = loopSequenceName(varName)
    counterName = loopVariableCounterName(varName)

    def loopIsLast(env):
        return (fetchProperty(env, counterName) == (len(fetchProperty(env, seqName)) - 1))

    return loopIsLast

def hasData(env):
    if isinstance(env, Env):
        return hasData(env.base)
    else:
        return len(env) > 0

def makeFunctionHandler(name, args):
    if name == 'hasData':
        return hasData
    elif name == 'index':
        return makeLoopIndex(args[0].name)
    elif name == 'isFirst':
        return makeLoopIsFirst(args[0].name)
    elif name == 'isLast':
        return makeLoopIsLast(args[0].name)

    funDict = { 'length': len,
                'keys': dict.keys,
                'round': ctRound,
                'floor': math.floor,
                'ceiling': math.ceil,
                'min': min,
                'max': max,
                'randomInt': lambda n: randint(0, n - 1)}

    fun = funDict[name]

    exprArgs =[makeExpressionHandler(arg) for arg in args]
    
    if not fun:
        raise Exception('Unknow function: %s' % name)

    def functionHandler(env):
        return fun(*[arg(env) for arg in exprArgs])

    return functionHandler

def makeExpressionHandler(expr):
    if isinstance(expr, Variable):
        return makeVariableHandler(expr.name)
    elif isinstance(expr, DotRef):
        return makeDotRefHandler(makeExpressionHandler(expr.expr),
                                 makeExpressionHandler(expr.name))
    elif isinstance(expr, ARef):
        return makeARefHandler(makeExpressionHandler(expr.expr),
                               makeExpressionHandler(expr.position))
    elif isinstance(expr, Operator):
        return makeOperatorHandler(expr.op, [makeExpressionHandler(arg) for arg in expr.args])
    elif isinstance(expr, Funcall):
        return makeFunctionHandler(expr.name, expr.args)
    else:
        return makeConstantlyHandler(expr)

####################################################################################################
# template handler
####################################################################################################

def writeTemplateAtom(obj, out):
    if isText(obj):
        out.write(obj)
    else:
        out.write(str(obj))

def makeCodeBlockHandler(block, autoescape):
    cmds = filter(None, block)

    for i in xrange(len(cmds)):
        if isinstance(cmds[i], Substition):
            cmds[i] = cmds[i].char
            
    commands = [makeCommandHandler(item, autoescape) for item in cmds]
    
    def codeBlockHandler(env, out, **kwargs):
        for cmd in filter(None, commands):
            cmd(env, out, **kwargs)

    return codeBlockHandler

def makePrintHandler(print_, autoescape):
    exprHandler = makeExpressionHandler(print_.expr)
    directives = print_.directives

    if autoescape and (directives.get('noAutoescape') != True):
        escapeHandler = escapeHtml
    else:
        escapeHandler = None

    if directives.get('escapeHtml'):
        escapeHandler = escapeHtml
    elif directives.get('id'):
        escapeHandler = encodeUriComponent
    elif directives.get('escapeUri'):
        escapeHandler = encodeUri

    if escapeHandler:
        def printHandler(env, out, **kwargs):
            writeTemplateAtom(escapeHandler(str(exprHandler(env))), out)
    else:
        def printHandler(env, out, **kwargs):
            writeTemplateAtom(exprHandler(env), out)

    return printHandler

def makeLiteralHandler(literal, autoescape):
    text = literal.text

    def literalHandler(env, out, **kwargs):
        writeTemplateAtom(text, out)

    return literalHandler

def makeIfHandler(if_, autoescape):
    options = [(makeExpressionHandler(item[0]), makeCodeBlockHandler(item[1], autoescape)) for item in if_]

    def ifHandler(env, out, **kwargs):
        for option in options:
            if option[0](env):
                option[1](env, out, **kwargs)
                return

    return ifHandler

def makeSwitchHandler(switch_, autoescape):
    expr = makeExpressionHandler(switch_.expr)

    def makeCaseItem(case):
        if isinstance(case, tuple):
            return (case[0], makeCommandHandler(case[1], autoescape))
        if isinstance(case, CodeBlock):
            return makeCommandHandler(case, autoescape)
        else:
            raise Exception('Bad of case')
    
    cases = [makeCaseItem(item) for item in switch_.cases]

    def switchHandler(env, out, **kwargs):
        value = expr(env)
        
        for case in cases:
            if isinstance(case, tuple):
                if value in case[0]:
                    case[1](env, out, **kwargs)
                    return
            else:
                case(env, out, **kwargs)

    return switchHandler

def makeForeachHandler(foreach_, autoescape):
    varName = foreach_.var.name
    exprHandler = makeExpressionHandler(foreach_.expr)
    bodyHandler = makeCommandHandler(foreach_.code, autoescape)
    
    if foreach_.ifEmptyCode:
        emptyHandler = makeCommandHandler(foreach_.ifEmptyCode, autoescape)

    def foreachHandler(env, out, **kwargs):
        r = exprHandler(env)

        if r:
            extra = { loopSequenceName(varName): r }
            counterName = loopVariableCounterName(varName)

            for i, value in enumerate(r):
                extra[varName] = value
                extra[counterName] = i
                bodyHandler(Env(env, extra), out, **kwargs)
        else:
            emptyHandler(env, out, **kwargs)

    return foreachHandler

def makeForHandler(for_, autoescape):
    varName = for_.var.name
    range_ = [makeExpressionHandler(item) for item in for_.range]
    bodyHandler = makeCommandHandler(for_.code, autoescape)

    def forHandler(env, out, **kwargs):
        for i in xrange(*[item(env) for item in range_]):
            bodyHandler(Env(env, {varName: i}), out, **kwargs)

    return forHandler

def makeCallHandler(call_, autoescape):
    templateNameHandler = makeExpressionHandler(call_.name)
    
    if call_.data == True:
        def dataHandler(env):
            return env
    elif call_.data == None:
        def dataHandler(env):
            return {}
    else:
        dataHandler = makeExpressionHandler(call_.data)

    def makeParamHandler(param):                
        if isinstance(param[1], CodeBlock):
            commandHandler = makeCommandHandler(param[1], autoescape)
            def paramHandler(env, ttable):
                out = StringIO()
                commandHandler(env, out, ttable=ttable)
                return out.getvalue()
        else:
            exprHandler = makeExpressionHandler(param[1])
            def paramHandler(env, ttable):
                return exprHandler(env)

        return (param[0], paramHandler)

    params = [makeParamHandler(param) for param in call_.params]

    def callHandler(env, out, ttable, **kwargs):
        newEnv = Env(dataHandler(env), {})

        for name, handler in params:
            newEnv.extra[name] = handler(env, ttable)
            
        ttable.callTemplate(templateNameHandler(env), newEnv, out)

    return callHandler
    
def makeCommandHandler(obj, autoescape):
    if isinstance(obj, CodeBlock):
        return makeCodeBlockHandler(obj, autoescape)
    if isinstance(obj, LiteralTag):
        return makeLiteralHandler(obj, autoescape)
    elif isinstance(obj, Print):
        return makePrintHandler(obj, autoescape)
    elif isinstance(obj, If):
        return makeIfHandler(obj, autoescape)
    elif isinstance(obj, Switch):
        return makeSwitchHandler(obj, autoescape)
    elif isinstance(obj, Foreach):
        return makeForeachHandler(obj, autoescape)
    elif isinstance(obj, For):
        return makeForHandler(obj, autoescape)
    elif isinstance(obj, Call):
        return makeCallHandler(obj, autoescape)
    elif isText(obj):
        def singleStringHandler(env, out, **kwargs):
            writeTemplateAtom(obj, out)
        return singleStringHandler
    else:
        return None

####################################################################################################
# namespace/template
####################################################################################################
    
def makeTemplateHandler(tmpl):
    name = tmpl.name
    props = tmpl.props

    codeBlockHandler = makeCodeBlockHandler(tmpl.code, not(props.get('autoescape') == False))

    def templateHandler(env, out, ttable):
        if out:
            codeBlockHandler(env, out, ttable=ttable)
        else:
            out = StringIO()
            codeBlockHandler(env, out, ttable=ttable)
            return out.getvalue()

    return templateHandler

def updateTTable(nameSpace, ttable):
    for tmpl in nameSpace.templates:
        ttable.registerTempalte(tmpl.name,
                                makeTemplateHandler(tmpl))

def makeTTable(nameSpace):
    ttable = TTable()
    updateTTable(nameSpace, ttable)
    return ttable

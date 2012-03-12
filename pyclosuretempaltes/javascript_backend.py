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

import json
from StringIO import StringIO
from contextlib import closing

from parser import *
from lepl import List


symbolCounter = 1

####################################################################################################
# helpers
####################################################################################################

class PrintParenthesis:
    def __init__(self, out, parenthesis='()'):
        self.parenthesis = parenthesis
        self.out = out
        
    def __enter__(self):
        self.out.write(self.parenthesis[0])

    def __exit__(self, exc_type, exc_value, traceback):
        if not exc_type:
            self.out.write(self.parenthesis[1])

class LocalVar:
    def __init__(self, name, localVars):
        self.localVars = localVars
        self.name = name

    def __enter__(self):
        self.localVars.append(self.name)

    def __exit__(self, exc_type, exc_value, traceback):
        if not exc_type:
            self.localVars.pop()

def js(text):
    return json.dumps(text)

####################################################################################################
# expressions
####################################################################################################

def writeDotRef(dot, namespace, localVars, out):
    writeExpression(dot.expr, namespace, localVars, out)

    if isinstance(dot.name, List):
        with PrintParenthesis(out, '[]'):
            writeExpression(dot.name, namespace, localVars, out)
    else:
        out.write('.%s' % dot.name)

def writeARef(aref, namespace, localVars, out):
    writeExpression(aref.expr, namespace, localVars, out)
    with PrintParenthesis(out, '[]'):
        writeExpression(aref.position, namespace, localVars, out)

def writeVariable(var, namespace, localVars, out):
    if not (var.name in localVars):
        out.write('$env$.')
    out.write(var.name)

def writeOperator(op, namespace, localVars, out):
    name = op.op
    args = op.args
    
    if len(args) == 1:
        if name == 'neg':
            out.write('-')
            writeExpression(op.args[0], namespace, localVars, out)
        elif name == 'not':
            out.write('!')
            writeExpression(op.args[0], namespace, localVars, out)
    elif len(args) == 2:
        if name == 'and':
            opName = '&&'
        elif name == 'or':
            opName = '||'
        else:
            opName = name

        with PrintParenthesis(out):
            writeExpression(args[0], namespace, localVars, out)
            out.write(' %s ' % opName)
            writeExpression(args[1], namespace, localVars, out)

    elif len(args) == 3:
        if name == 'if':
            with PrintParenthesis(out):
                writeExpression(args[0], namespace, localVars, out)
                out.write(' ? ')
                writeExpression(args[1], namespace, localVars, out)
                out.write(' : ')
                writeExpression(args[2], namespace, localVars, out)

def writeFuncall(expr, namespace, localVars, out):
    name = expr.name
    args = expr.args

    def writeSimpleFuncall(funName):
        out.write(funName)

        with PrintParenthesis(out):
            writeExpression(expr.args[0], namespace, localVars, out)

            for arg in expr.args[1:]:
                out.write(', ')
                writeExpression(arg, namespace, localVars, out)
        
    
    if name == 'hasData':
        out.write('($env$ && !%s.$isEmpty$($env$))' % namespace)
    elif name == 'index':
        out.write('($counter_%s$ + 1)' % args[0].name)
    elif name == 'isFirst':
        out.write('($counter_%s$ == 0)' % args[0].name)
    elif name == 'isLast':
        out.write('($counter_%s$ == ($sequence_%s$.length - 1))' % (args[0].name, args[0].name))
    elif name == 'randomInt':
        out.write('Math.floor')
        with PrintParenthesis(out):
            out.write('Math.random() * ')
            writeExpression(args[0], namespace, localVars, out)
    elif name == 'round':
        writeSimpleFuncall('%s.$round$' % namespace)
    else:
        writeSimpleFuncall('Math.%s' % name)

def writeExpression(expr, namespace, localVars, out):
    if isinstance(expr, Variable):
        writeVariable(expr, namespace, localVars, out)
    elif isinstance(expr, DotRef):
        writeDotRef(expr, namespace, localVars, out)
    elif isinstance(expr, ARef):
        writeARef(expr, namespace, localVars, out)
    elif isinstance(expr, Operator):
        writeOperator(expr, namespace, localVars, out)
    elif isinstance(expr, Funcall):
        writeFuncall(expr, namespace, localVars, out)
    else:
        out.write(js(expr))

####################################################################################################
# commands
####################################################################################################

def writeIndent(indentLevel, out):
    out.write(' ' * 4 * indentLevel)

# CodeBlock

def writeCodeBlock(block, autoescape, namespace, localVars, indentLevel, out):
    cmds = filter(None, block)

    for i in xrange(len(cmds)):
        if isinstance(cmds[i], Substition):
            char = block[i].char
            
            if char == ' ':
                cmds[i] = ' '
            elif char == '\r':
                cmds[i] = '\\r'
            elif char == '\n':
                cmds[i] = '\\n'
            elif char == '\t':
                cmds[i] = '\\t'
            elif char == '{' or char == '}':
                cmds[i] = char
            elif char == '':
                cmds[i] = None
            else:
                raise char
                cmds[i] = None
            

    for cmd in filter(None, cmds):
        writeCommand(cmd, autoescape, namespace, localVars, indentLevel, out)

# Literal

def writeLiteral(literal, autoescape, namespace, localVars, indentLevel, out):
    writeIndent(indentLevel, out)
    out.write('$result$.push(%s);\n' % js(literal.text))


# Print

def writePrint(print_, autoescape, namespace, localVars, indentLevel, out):
    writeIndent(indentLevel, out)
    out.write('$result$.push')

    directives = print_.directives
    
    with PrintParenthesis(out):
        if directives.get('id'):
            out.write('encodeURIComponent')
            with PrintParenthesis(out):
                writeExpression(print_.expr, namespace, localVars, out)
        elif directives.get('escapeUri'):
            out.write('encodeURI')
            with PrintParenthesis(out):
                writeExpression(print_.expr, namespace, localVars, out)
        elif directives.get('escapeHtml') or (autoescape and (directives.get('noAutoescape') != True)):
            out.write('%s.$escapeHTML$' % namespace)
            with PrintParenthesis(out):
                writeExpression(print_.expr, namespace, localVars, out)
        else:
            writeExpression(print_.expr, namespace, localVars, out)

    out.write(';\n')

# If

def writeIf(if_, autoescape, namespace, localVars, indentLevel, out):
    first = True
    for option in if_:
        writeIndent(indentLevel, out)
        if first:
            out.write('if ')
            first = False
            with PrintParenthesis(out):
                writeExpression(option[0], namespace, localVars, out)
        elif option[0] == True:
            out.write('else')
        else:
            out.write('else if ')
            with PrintParenthesis(out):
                writeExpression(option[0], namespace, localVars, out)
        out.write(' {\n')

        writeCommand(option[1], autoescape, namespace, localVars, indentLevel + 1, out)

        writeIndent(indentLevel, out)
        out.write('}\n')

# Switch

def writeSwitch(switch_, autoescape, namespace, localVars, indentLevel, out):
    writeIndent(indentLevel, out)
    out.write('switch ')
    with PrintParenthesis(out):
        writeExpression(switch_.expr, namespace, localVars, out)
    out.write(' {\n')

    for case in switch_.cases:
        if isinstance(case, tuple):
            for item in case[0]:
                writeIndent(indentLevel + 1, out)
                out.write('case ')
                writeExpression(item, namespace, localVars, out)
                out.write(':\n')

            writeCommand(case[1], autoescape, namespace, localVars, indentLevel + 2, out)
            writeIndent(indentLevel + 2, out)
            out.write('break;\n')
        else:
            writeIndent(indentLevel + 1, out)
            out.write('default:\n')

            writeCommand(case, autoescape, namespace, localVars, indentLevel + 2, out)
            writeIndent(indentLevel + 2, out)
            out.write('break;\n')

    writeIndent(indentLevel, out)
    out.write('}\n')


# Foreach

def writeForeach(foreach_, autoescape, namespace, localVars, indentLevel, out):
    varName = foreach_.var.name
    seqName = '$sequence_%s$' % varName
    counterName = '$counter_%s$' % varName

    writeIndent(indentLevel, out)
    out.write('var %s = ' % seqName)
    writeExpression(foreach_.expr, namespace, localVars, out)
    out.write(';\n')

    writeIndent(indentLevel, out)
    out.write('if (%s) {\n' % seqName)
    
    writeIndent(indentLevel + 1, out)
    out.write('for (var %s = 0; %s < %s.length; ++%s) {\n' % (counterName, counterName, seqName, counterName))

    writeIndent(indentLevel + 2, out)
    out.write('var %s = %s[%s];\n' % (varName, seqName, counterName))

    with LocalVar(varName, localVars):
        writeCommand(foreach_.code, autoescape, namespace, localVars, indentLevel + 2, out)

    writeIndent(indentLevel + 1, out)
    out.write('}\n')

    writeIndent(indentLevel, out)
    out.write('}\n')

    if foreach_.ifEmptyCode:
        writeIndent(indentLevel, out)
        out.write('else {\n')

        writeCommand(foreach_.ifEmptyCode, autoescape, namespace, localVars, indentLevel + 1, out)

        writeIndent(indentLevel, out)
        out.write('}\n')

# For

def writeFor(for_, autoescape, namespace, localVars, indentLevel, out):
    varName = for_.var.name
    range_ = for_.range

    writeIndent(indentLevel, out)
    if len(range_) == 1:
        out.write('for (var %s = 0; %s < ' % (varName, varName))
        writeExpression(range_[0], namespace, localVars, out)
        out.write('; ++%s) {\n' % varName)
    elif len(range_) == 2:
        out.write('for (var %s = ' % varName)
        writeExpression(range_[0], namespace, localVars, out)
        out.write('; %s < ' % varName)
        writeExpression(range_[1], namespace, localVars, out)
        out.write('; ++%s) {\n' % varName)
    elif len(range_) == 3:
        out.write('for (var %s = ' % varName)
        writeExpression(range_[0], namespace, localVars, out)
        out.write('; %s < ' % varName)
        writeExpression(range_[1], namespace, localVars, out)
        out.write('; %s += ' % varName)
        writeExpression(range_[2], namespace, localVars, out)
        out.write(') {\n')

    with LocalVar(varName, localVars):
        writeCommand(for_.code, autoescape, namespace, localVars, indentLevel + 1, out)

    writeIndent(indentLevel, out)
    out.write('}\n')

def writeCall(call_, autoescape, namespace, localVars, indentLevel, out):
    if call_.params:
        global symbolCounter;

        symbolCounter += 1
        newEnvName = '$env_%s$' % symbolCounter

        writeIndent(indentLevel, out)
        out.write('var %s = ' % newEnvName)

        if call_.data == True:
            out.write('%s.$objectFromPrototype$($env$)' % namespace)
        elif call_.data == None:
            out.write('{}')
        else:
            out.write('%s.$objectFromPrototype$' % namespace)
            with PrintParenthesis(out):
                writeExpression(call_.data, namespace, localVars, out)
            
        out.write(';\n')

        for param in call_.params:
            if isinstance(param[1], CodeBlock):
                symbolCounter += 1
                
                writeIndent(indentLevel, out)
                out.write('%s.%s = function () {\n' % (newEnvName, param[0]))

                writeIndent(indentLevel + 1, out)
                out.write('var $result$ = [];\n')
    
                writeCommand(param[1], autoescape, namespace, localVars, indentLevel + 1, out)

                writeIndent(indentLevel + 1, out)
                out.write('return $result$.join("");\n')

                writeIndent(indentLevel, out)
                out.write('}();\n')
            else:
                writeIndent(indentLevel, out)
                out.write('%s.%s = ' % (newEnvName, param[0]))
                writeExpression(param[1], namespace, localVars, out)
                out.write(';\n')

        writeIndent(indentLevel, out)
        if isText(call_.name):
            out.write('%s.%s' % (namespace, call_.name))
        else:
            out.write(namespace)
            with PrintParenthesis(out, '[]'):
                writeExpression(call_.name, namespace, localVars, out)
        
        out.write('(%s, $result$);\n' % (newEnvName))
    else:
        writeIndent(indentLevel, out)

        if isText(call_.name):
            out.write('%s.%s' % (namespace, call_.name))
        else:
            out.write(namespace)
            with PrintParenthesis(out, '[]'):
                writeExpression(call_.name, namespace, localVars, out)

        with PrintParenthesis(out):
            if call_.data == True:
                out.write('$env$')
            elif call_.data == None:
                out.write('{}')
            else:
                writeExpression(call_.data, namespace, localVars, out)

            out.write(', $result$')
        out.write(';\n')


# All Commands
        
def writeCommand(cmd, autoescape, namespace, localVars, indentLevel, out):
    if isinstance(cmd, CodeBlock):
        writeCodeBlock(cmd, autoescape, namespace, localVars, indentLevel, out)
    elif isinstance(cmd, LiteralTag):
        writeLiteral(cmd, autoescape, namespace, localVars, indentLevel, out)
    elif isinstance(cmd, Print):
        writePrint(cmd, autoescape, namespace, localVars, indentLevel, out)
    elif isinstance(cmd, If):
        writeIf(cmd, autoescape, namespace, localVars, indentLevel, out)
    elif isinstance(cmd, Switch):
        writeSwitch(cmd, autoescape, namespace, localVars, indentLevel, out)
    elif isinstance(cmd, Foreach):
        writeForeach(cmd, autoescape, namespace, localVars, indentLevel, out)
    elif isinstance(cmd, For):
        writeFor(cmd, autoescape, namespace, localVars, indentLevel, out)
    elif isinstance(cmd, Call):
        writeCall(cmd, autoescape, namespace, localVars, indentLevel, out)
    elif isText(cmd):
        writeIndent(indentLevel, out)
        out.write('$result$.push')
        with PrintParenthesis(out):
            out.write(js(cmd))
        out.write(';\n')

####################################################################################################
# namespace/template
####################################################################################################
    
def writeTemplate(tmpl, namespace,  out):
    out.write('\n%s.%s = function($env$, $target$) {\n' % (namespace, tmpl.name))
    writeIndent(1, out)
    out.write('if (!$env$) { $env$ = {}; }\n')

    writeIndent(1, out)
    out.write('var $result$ = $target$ || [];\n\n')
    
    writeCommand(tmpl.code, not(tmpl.props.get('autoescape') == False), namespace, [], 1, out)

    out.write('\n')
    writeIndent(1, out)
    out.write('if (!$target$) return $result$.join("");\n')
    writeIndent(1, out)
    out.write('else return null;\n');
    
    out.write('};\n')

def writeNamespace(namespace, out):
    name = namespace.name

    nameParts = name.split('.')

    for i in range(len(nameParts)):
        shortName = '.'.join(nameParts[0:i+1])
        out.write("if (typeof %s == 'undefined') { %s = {}; }\n" % (shortName, shortName))


    # hasData
    out.write('\n%s.%s = function(obj) {\n' % (name, '$isEmpty$'))
    out.write('    for (var prop in obj) if (obj.hasOwnProperty(prop)) return false;\n')
    out.write('    return true;')
    out.write('\n};\n')

    # escapeHTML
    out.write('\n%s.%s = function(obj) {\n' % (name, '$escapeHTML$'))
    out.write('    if (typeof obj == \'string\') return String(obj)')
    out.write('.split("&").join("&amp;")')
    out.write('.split( "<").join("&lt;")')
    out.write('.split(">").join("&gt;")')
    out.write('.split("\\"").join("&quot;")')
    out.write('.split("\'").join("&#039;")')
    out.write(';\n')
    out.write('    else return obj;')
    out.write('\n};\n')

    # round
    out.write('\n%s.%s = function(number, ndigits) {\n' % (name, '$round$'))
    out.write('    if (ndigits) {\n')
    out.write('        var factor = Math.pow(10.0, ndigits);\n')
    out.write('        return Math.round(number * factor) / factor;\n')
    out.write('    }\n')
    out.write('    else return Math.round(number);')
    out.write('\n};\n')

    # objectFromPrototype
    out.write('\n%s.%s = function(obj) {\n' % (name, '$objectFromPrototype$'))
    out.write('    function C () {}\n')
    out.write('    C.prototype = obj;\n')
    out.write('    return new C;')
    out.write('\n};\n')
    
    for tmpl in namespace.templates:
        writeTemplate(tmpl, name, out)

def compileNamespaceToJS(namespace):
    with closing(StringIO()) as out:
        writeNamespace(namespace, out)
        return out.getvalue()

def compileToJS(path):
    return compileNamespaceToJS(parseFile(path))

####################################################################################################
# main
####################################################################################################

if __name__ == "__main__":
    namespace = parseNamespace("""
    {namespace merchandising.view}

    {template helloWorld}
       Hello world!
    {/template}

    {template helloName}
       Hello {$name}
    {/template}

    """)

    with closing(StringIO()) as out:
        writeNamespace(namespace, [], out)
        print out.getvalue()

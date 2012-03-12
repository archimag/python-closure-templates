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

import unittest
import sys

sys.path[0:0] = [""]

from pyclosuretempaltes.parser import *

class TestExpressionParser(unittest.TestCase):
    def setUp(self):
        pass

    def testLiterals(self):
        self.assertEqual(parseExpression("'Hello world'"), 'Hello world')
        print parseExpression("''")
        self.assertEqual(parseExpression("''"), '')
        self.assertEqual(parseExpression("5"), 5)
        self.assertEqual(parseExpression("3.14"), 3.14)

    def testVars(self):
        a = parseExpression(' $var ')
        self.assertIsInstance(a, Variable)
        self.assertEqual(a.name, 'var')

        b = parseExpression('$x.y')
        self.assertIsInstance(b, DotRef)
        self.assertEqual(b.name, 'y')
        self.assertIsInstance(b.expr, Variable)
        self.assertEqual(b.expr.name, 'x')

        c = parseExpression('$x.1.y')
        self.assertIsInstance(c, DotRef)
        self.assertEqual(c.name, 'y')
        self.assertIsInstance(c.expr, ARef)
        self.assertEqual(c.expr.position, 1)
        self.assertIsInstance(c.expr.expr, Variable)
        self.assertEqual(c.expr.expr.name, 'x')

        d = parseExpression('$x[0].y')
        self.assertIsInstance(d, DotRef)
        self.assertEqual(d.name, 'y')
        self.assertIsInstance(d.expr, ARef)
        self.assertEqual(d.expr.position, 0)
        self.assertIsInstance(d.expr.expr, Variable)
        self.assertEqual(d.expr.expr.name, 'x')

        e = parseExpression('$x[$z].y')
        self.assertIsInstance(e, DotRef)
        self.assertEqual(e.name, 'y')
        self.assertIsInstance(e.expr, ARef)
        self.assertIsInstance(e.expr.position, Variable)
        self.assertEqual(e.expr.position.name, 'z')
        self.assertIsInstance(e.expr.expr, Variable)
        self.assertEqual(e.expr.expr.name, 'x')

        f = parseExpression('$x[0][1]')
        self.assertIsInstance(f, ARef)
        self.assertEqual(f.position, 1)
        self.assertIsInstance(f.expr, ARef)
        self.assertEqual(f.expr.position, 0)
        self.assertIsInstance(f.expr.expr, Variable)
        self.assertEqual(f.expr.expr.name, 'x')

        g = parseExpression('$x[0][1][$y]')
        self.assertIsInstance(g, ARef)
        self.assertIsInstance(g.position, Variable)
        self.assertEqual(g.position.name, 'y')
        self.assertIsInstance(g.expr, ARef)
        self.assertEqual(g.expr.position, 1)
        self.assertIsInstance(g.expr.expr, ARef)
        self.assertEqual(g.expr.expr.position, 0)
        self.assertIsInstance(g.expr.expr.expr, Variable)
        self.assertEqual(g.expr.expr.expr.name, 'x')

    def testOperators(self):
        a = parseExpression('-$x')
        self.assertIsInstance(a, Operator)
        self.assertEqual(a.op, 'neg')
        self.assertIsInstance(a.args[0], Variable)
        self.assertEqual(a.args[0].name, 'x')

        b = parseExpression('not $x')
        self.assertIsInstance(b, Operator)
        self.assertEqual(b.op, 'not')
        self.assertIsInstance(b.args[0], Variable)
        self.assertEqual(b.args[0].name, 'x')

        c = parseExpression(' $x + $y ')
        self.assertIsInstance(c, Operator)
        self.assertEqual(c.op, '+')
        self.assertEqual(len(c.args), 2)
        self.assertIsInstance(c.args[0], Variable)
        self.assertEqual(c.args[0].name, 'x')
        self.assertIsInstance(c.args[1], Variable)
        self.assertEqual(c.args[1].name, 'y')

        d = parseExpression('2 + 2')
        self.assertIsInstance(d, Operator)
        self.assertEqual(d.args, [2, 2])

        e = parseExpression(' $x - $y ')
        self.assertIsInstance(e, Operator)
        self.assertEqual(e.op, '-')
        self.assertEqual(len(e.args), 2)
        self.assertIsInstance(e.args[0], Variable)
        self.assertEqual(e.args[0].name, 'x')
        self.assertIsInstance(e.args[1], Variable)
        self.assertEqual(e.args[1].name, 'y')

        self.assertEqual(parseExpression(' $x * $y ').op, '*')
        self.assertEqual(parseExpression(' $x/$y ').op, '/')
        self.assertEqual(parseExpression(' $x % $y ').op, '%')
        self.assertEqual(parseExpression('$x > $y').op, '>')
        self.assertEqual(parseExpression('$x < $y').op, '<')
        self.assertEqual(parseExpression('$x>=$y').op, '>=')
        self.assertEqual(parseExpression('$x<=$y').op, '<=')
        self.assertEqual(parseExpression('$x==$y').op, '==')
        self.assertEqual(parseExpression('$x!=$y').op, '!=')
        self.assertEqual(parseExpression('$x and $y').op, 'and')
        self.assertEqual(parseExpression('$x or $y').op, 'or')

        #f = parseExpression('28 - 2 + (3 + 4)')
        #self.assertIsInstance(

    def testTernaryOperator(self):
        a = parseExpression("max(2, $x ? min($x, $y ? 3 : 5 + 4, 6) : 4)")
        self.assertIsInstance(a, Funcall)
        self.assertEqual(a.name, 'max')
        self.assertEqual(a.args[0], 2)

        b = a.args[1]
        self.assertIsInstance(b, Operator)
        self.assertEqual(b.op, 'if')
        self.assertIsInstance(b.args[0], Variable)
        self.assertEqual(b.args[0].name, 'x')
        self.assertEqual(b.args[2], 4)

        c = b.args[1]
        self.assertIsInstance(c, Funcall)
        self.assertEqual(c.name, 'min')
        self.assertIsInstance(c.args[0], Variable)
        self.assertEqual(c.args[0].name, 'x')
        self.assertEqual(c.args[2], 6)

        d = c.args[1]
        self.assertIsInstance(d, Operator)
        self.assertEqual(d.op, 'if')
        self.assertIsInstance(d.args[0], Variable)
        self.assertEqual(d.args[0].name, 'y')
        self.assertEqual(d.args[1], 3)

        e = d.args[2]
        self.assertIsInstance(e, Operator)
        self.assertEqual(e.op, '+')
        self.assertEqual(e.args, [5, 4])
        
    def testFunctions(self):
        a = parseExpression("hasData()")
        self.assertIsInstance(a, Funcall)
        self.assertEqual(a.name, 'hasData')
        self.assertEqual(a.args, [])

        b = parseExpression('min($x, $y)')
        self.assertIsInstance(b, Funcall)
        self.assertEqual(b.name, 'min')
        self.assertIsInstance(b.args[0], Variable)
        self.assertEqual(b.args[0].name, 'x')
        self.assertIsInstance(b.args[1], Variable)
        self.assertEqual(b.args[1].name, 'y')

        c = parseExpression('min($x, max(5, $y))')
        self.assertIsInstance(c, Funcall)
        self.assertEqual(c.name, 'min')
        self.assertIsInstance(c.args[0], Variable)
        self.assertEqual(c.args[0].name, 'x')
        self.assertIsInstance(c.args[1], Funcall)
        self.assertEqual(c.args[1].name, 'max')
        self.assertEqual(c.args[1].args[0], 5)
        self.assertIsInstance(c.args[1].args[1], Variable)
        self.assertEqual(c.args[1].args[1].name, 'y')

class TestCommandParser(unittest.TestCase):
    def setUp(self):
        pass

    def testTemplateProps(self):
        a = parseSingleTemplate('{template testA autoescape="true"}{/template}')
        self.assertIsInstance(a, Template)
        self.assertEqual(a.name, 'testA')
        self.assertEqual(a.props.get('autoescape'), True)

        b = parseSingleTemplate('{template testB private="false"}{/template}')
        self.assertIsInstance(b, Template)
        self.assertEqual(b.name, 'testB')
        self.assertEqual(b.props.get('private'), False)

        c = parseSingleTemplate('{template testC autoescape="false" private="true"}{/template}')
        self.assertIsInstance(c, Template)
        self.assertEqual(c.name, 'testC')
        self.assertEqual(c.props.get('autoescape'), False)
        self.assertEqual(c.props.get('private'), True)

        d = parseSingleTemplate("""{template testD}
            Hello
        {/template}""")
        self.assertIsInstance(d, Template)
        self.assertEqual(d.name, 'testD')
        self.assertEqual(d.props.get('autoescape'), None)
        self.assertEqual(d.props.get('private'), None)
        self.assertIsInstance(d.code, CodeBlock)
        self.assertEqual(d.code[0], 'Hello')

    def testSubstitions(self):
        a = parseSingleTemplate('{template substitions}{sp}{nil}{\\r}{\\n}{\\t}{lb}{rb}{/template}')
        self.assertIsInstance(a, Template)
        self.assertEqual(a.name, 'substitions')
        self.assertIsInstance(a.code, CodeBlock)
        self.assertEqual(''.join([item.char for item in a.code]), ' \r\n\t{}')

    def testPrint(self):
        a = parseSingleTemplate('{template helloName}Hello {$name}{/template}')
        self.assertIsInstance(a, Template)
        self.assertEqual(a.name, 'helloName')
        self.assertIsInstance(a.code, CodeBlock)
        self.assertEqual(a.code[0], 'Hello ')
        self.assertIsInstance(a.code[1], Print)
        self.assertIsInstance(a.code[1].expr, Variable)
        self.assertEqual(a.code[1].expr.name, 'name')

        b = parseSingleTemplate('{template test}{2 + 2}{/template}')
        self.assertIsInstance(b, Template)
        self.assertEqual(b.name, 'test')
        self.assertIsInstance(b.code, CodeBlock)
        self.assertIsInstance(b.code[0], Print)
        self.assertIsInstance(b.code[0].expr, Operator)
        self.assertEqual(b.code[0].expr.op, '+')
        self.assertEqual(b.code[0].expr.args, [2, 2])

        c = parseSingleTemplate('{template test}{2 + 2 |noAutoescape}{/template}')
        self.assertIsInstance(c, Template)
        self.assertEqual(c.name, 'test')
        self.assertIsInstance(c.code, CodeBlock)
        self.assertIsInstance(c.code[0], Print)
        self.assertIsInstance(c.code[0].expr, Operator)
        self.assertEqual(c.code[0].expr.op, '+')
        self.assertEqual(c.code[0].expr.args, [2, 2])
        self.assertEqual(c.code[0].directives.get('noAutoescape'), True)

        d = parseSingleTemplate('{template test}{2 + 2 |id}{/template}')
        self.assertIsInstance(d, Template)
        self.assertEqual(d.name, 'test')
        self.assertIsInstance(d.code, CodeBlock)
        self.assertIsInstance(d.code[0], Print)
        self.assertIsInstance(d.code[0].expr, Operator)
        self.assertEqual(d.code[0].expr.op, '+')
        self.assertEqual(d.code[0].expr.args, [2, 2])
        self.assertEqual(d.code[0].directives.get('noAutoescape'), None)
        self.assertEqual(d.code[0].directives.get('id'), True)

        e = parseSingleTemplate("""{template test}
           {2 + 2 |noAutoescape |id |escapeHtml |escapeUri |escapeJs  |insertWordBreaks:5}
        {/template}""")
        self.assertIsInstance(e, Template)
        self.assertEqual(e.name, 'test')
        self.assertIsInstance(e.code, CodeBlock)
        self.assertIsInstance(e.code[0], Print)
        self.assertIsInstance(e.code[0].expr, Operator)
        self.assertEqual(e.code[0].expr.op, '+')
        self.assertEqual(e.code[0].expr.args, [2, 2])
        self.assertEqual(e.code[0].directives.get('noAutoescape'), True)
        self.assertEqual(e.code[0].directives.get('id'), True)
        self.assertEqual(e.code[0].directives.get('escapeHtml'), True)
        self.assertEqual(e.code[0].directives.get('escapeUri'), True)
        self.assertEqual(e.code[0].directives.get('escapeJs'), True)
        self.assertEqual(e.code[0].directives.get('insertWordBreaks'), 5)

    def testLiteral(self):
        a = parseSingleTemplate('{template literalTest}{literal}Test {$x} {foreach $foo in $bar}{$foo}{/foreach}{/literal}{/template}')
        self.assertIsInstance(a, Template)
        self.assertEqual(a.name, 'literalTest')
        self.assertIsInstance(a.code, CodeBlock)
        self.assertIsInstance(a.code[0], LiteralTag)
        self.assertEqual(a.code[0].text, 'Test {$x} {foreach $foo in $bar}{$foo}{/foreach}')

    def testIf(self):
        a = parseSingleTemplate('{template ifTest}{if $x}Hello {$x}{/if}{/template}')
        self.assertIsInstance(a, Template)
        self.assertEqual(a.name, 'ifTest')
        self.assertIsInstance(a.code, CodeBlock)
        self.assertEqual(len(a.code), 1)
        self.assertIsInstance(a.code[0], If)
        self.assertIsInstance(a.code[0][0][0], Variable)
        self.assertEqual(a.code[0][0][0].name, 'x')
        self.assertIsInstance(a.code[0][0][1], CodeBlock)
        self.assertEqual(a.code[0][0][1][0], 'Hello ')
        self.assertIsInstance(a.code[0][0][1][1], Print)
        self.assertIsInstance(a.code[0][0][1][1].expr, Variable)
        self.assertEqual(a.code[0][0][1][1].expr.name, 'x')

        b = parseSingleTemplate('{template ifTest}{if $x}Hello {$x}{elseif $y}By {$y}{else}Hello world{/if}{/template}').code[0]
        self.assertIsInstance(b, If)
        self.assertIsInstance(b[0][0], Variable)
        self.assertEqual(b[0][0].name, 'x')
        self.assertEqual(b[0][1][0], 'Hello ')
        self.assertIsInstance(b[0][1][1], Print)
        self.assertIsInstance(b[0][1][1].expr, Variable)
        self.assertEqual(b[0][1][1].expr.name, 'x')
        self.assertIsInstance(b[1][0], Variable)
        self.assertEqual(b[1][0].name, 'y')
        self.assertEqual(b[1][1][0], 'By ')
        self.assertIsInstance(b[1][1][1], Print)
        self.assertIsInstance(b[1][1][1].expr, Variable)
        self.assertEqual(b[1][1][1].expr.name, 'y')
        self.assertEqual(b[2][0], True)
        self.assertEqual(b[2][1][0], 'Hello world')

    def testSwitch1(self):
        a = parseSingleTemplate('{template switchTest}{switch $x}{case 1}hello world{case 2, 3, 4}by-by{/switch}{/template}')
        self.assertIsInstance(a, Template)
        self.assertEqual(a.name, 'switchTest')
        self.assertIsInstance(a.code, CodeBlock)

        b = a.code[0]
        self.assertIsInstance(b, Switch)
        self.assertIsInstance(b.expr, Variable)
        self.assertEqual(b.expr.name, 'x')

        self.assertEqual(b.cases[0][0], [1])
        self.assertEqual(list(b.cases[0][1]), ['hello world'])
        self.assertEqual(b.cases[1][0], [2, 3, 4])
        self.assertEqual(list(b.cases[1][1]), ['by-by'])
        
    def testForeach(self):
        a = parseSingleTemplate('{template test}{foreach $x in $y.foo }{$x}{ifempty}Hello{/foreach}{/template}')
        self.assertIsInstance(a, Template)
        self.assertEqual(a.name, 'test')
        self.assertIsInstance(a.code, CodeBlock)

        b = a.code[0]
        self.assertIsInstance(b, Foreach)
        self.assertIsInstance(b.var, Variable)
        self.assertEqual(b.var.name, 'x')

        self.assertIsInstance(b.expr, DotRef)
        self.assertEqual(b.expr.name, 'foo')
        self.assertIsInstance(b.expr.expr, Variable)
        self.assertEqual(b.expr.expr.name, 'y')

        c = b.code
        self.assertIsInstance(c, CodeBlock)
        self.assertIsInstance(c[0], Print)
        self.assertIsInstance(c[0].expr, Variable)
        self.assertEqual(c[0].expr.name, 'x')

        d = b.ifEmptyCode
        self.assertIsInstance(d, CodeBlock)
        self.assertEqual(d[0], 'Hello')
        

    def testFor(self):
        a = parseSingleTemplate('{template test}{for $x in range(10)} ! {/for}{/template}')
        self.assertIsInstance(a, Template)
        self.assertEqual(a.name, 'test')
        self.assertIsInstance(a.code, CodeBlock)
        self.assertIsInstance(a.code[0], For)
        self.assertEqual(a.code[0].range, [10])
        self.assertEqual(a.code[0].code[0], '!')

        b = parseSingleTemplate('{template test}{for $x in range(4, 10)} ! {/for}{/template}')
        self.assertIsInstance(b, Template)
        self.assertEqual(b.name, 'test')
        self.assertIsInstance(b.code, CodeBlock)
        self.assertIsInstance(b.code[0], For)
        self.assertEqual(b.code[0].range, [4, 10])
        self.assertEqual(b.code[0].code[0], '!')

        c = parseSingleTemplate('{template test}{for $x in range(4, 10, 2)} ! {/for}{/template}')
        self.assertIsInstance(c, Template)
        self.assertEqual(c.name, 'test')
        self.assertIsInstance(c.code, CodeBlock)
        self.assertIsInstance(c.code[0], For)
        self.assertEqual(c.code[0].range, [4, 10, 2])
        self.assertEqual(c.code[0].code[0], '!')

    def testCall(self):
        a = parseSingleTemplate('{template test}{call helloName1 data=\"$x\" /}{/template}')
        self.assertIsInstance(a.code[0], Call)
        self.assertEqual(a.code[0].name, 'helloName1')
        self.assertIsInstance(a.code[0].data, Variable)
        self.assertEqual(a.code[0].data.name, 'x')
        self.assertEqual(a.code[0].params, [])

        b = parseSingleTemplate('{template test}{call helloName2}{param name: $x /}{/call}{/template}')
        self.assertIsInstance(b.code[0], Call)
        self.assertEqual(b.code[0].name, 'helloName2')
        self.assertEqual(b.code[0].data, None)
        self.assertEqual(len(b.code[0].params), 1)
        self.assertEqual(b.code[0].params[0][0], 'name')
        self.assertIsInstance(b.code[0].params[0][1], Variable)
        self.assertEqual(b.code[0].params[0][1].name, 'x')

        c = parseSingleTemplate("""{template test}
           {call helloName3 data=\"$data\"}
               {param a: $x /}
               {param b}Hello {$y}{/param}
           {/call}
        {/template}""")
        self.assertIsInstance(c.code[0], Call)
        self.assertEqual(c.code[0].name, 'helloName3')
        self.assertIsInstance(c.code[0].data, Variable)
        self.assertEqual(c.code[0].data.name, 'data')
        self.assertEqual(len(c.code[0].params), 2)
        self.assertEqual(c.code[0].params[0][0], 'a')
        self.assertIsInstance(c.code[0].params[0][1], Variable)
        self.assertEqual(c.code[0].params[0][1].name, 'x')
        self.assertEqual(c.code[0].params[1][0], 'b')
        self.assertIsInstance(c.code[0].params[1][1], CodeBlock)
        self.assertEqual(c.code[0].params[1][1][0], 'Hello ')
        self.assertIsInstance(c.code[0].params[1][1][1], Print)
        self.assertIsInstance(c.code[0].params[1][1][1].expr, Variable)
        self.assertEqual(c.code[0].params[1][1][1].expr.name, 'y')

        d = parseSingleTemplate('{template test}{call name=\"$name\"  /}{/template}')
        self.assertIsInstance(d.code[0], Call)
        self.assertIsInstance(d.code[0].name, Variable)
        self.assertEqual(d.code[0].name.name, 'name')
        self.assertEqual(d.code[0].data, None)
        self.assertEqual(d.code[0].params, [])

        e = parseSingleTemplate('{template test}{call name=\"$x\" data=\"all\"  /}{/template}')
        self.assertIsInstance(e.code[0], Call)
        self.assertIsInstance(e.code[0].name, Variable)
        self.assertEqual(e.code[0].name.name, 'x')
        self.assertEqual(e.code[0].data, True)
        self.assertEqual(e.code[0].params, [])

    # def testWhitespaces(self):
    #     pass
        

if __name__ == "__main__":
    unittest.main()

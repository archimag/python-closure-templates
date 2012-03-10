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

from pyclosuretempaltes.parser import parseNamespace
from pyclosuretempaltes.python_backend import makeTTable

class TestPythonBackend(unittest.TestCase):
    def setUp(self):
        pass

    def testSimple(self):
        nameSpace = parseNamespace("""
        {namespace test}

        {template helloWorld1}
           Hello world!
        {/template}
    
        {template helloWorld2}
          <Hello world>
        {/template}""")

        ttable = makeTTable(nameSpace)

        self.assertEqual(ttable.callTemplate('helloWorld1', {}), 'Hello world!')
        self.assertEqual(ttable.callTemplate('helloWorld2', {}), '<Hello world>')

    def testPrint(self):
        nameSpace = parseNamespace("""
        {namespace test}

        {template testPrint1}
            {$arg}
        {/template}
    
        {template testPrint2 autoescape=\"false\"}
            {$arg}
        {/template}

        {template testPrint3}
            {$arg|noAutoescape}
        {/template}

        {template testPrint4}
            {$arg |escapeUri}
        {/template}

        {template testPrint5}
            {$arg | id}
        {/template}

        {template testPrint6 autoescape=\"false\"}
            {$arg |escapeHtml}
        {/template}
        
        """)

        ttable = makeTTable(nameSpace)

        self.assertEqual(ttable.callTemplate('testPrint1', {'arg': '<&\"\'>'}),
                         '&lt;&amp;&quot;&#039;&gt;')
        self.assertEqual(ttable.callTemplate('testPrint2', {'arg': '<&\"\'>'}),
                         '<&\"\'>')
        self.assertEqual(ttable.callTemplate('testPrint3', {'arg': '<&\"\'>'}),
                         '<&\"\'>')
        self.assertEqual(ttable.callTemplate('testPrint4', {'arg': '~!@#$%^&*(){}[]=:/,;?+\'\"\\'}),
                         '~!@#$%25%5E&*()%7B%7D%5B%5D=:/,;?+\'%22%5C')
        self.assertEqual(ttable.callTemplate('testPrint5', {'arg': '~!@#$%^&*(){}[]=:/,;?+\'\"\\'}),
                         '~!%40%23%24%25%5E%26*()%7B%7D%5B%5D%3D%3A%2F%2C%3B%3F%2B\'%22%5C')
        self.assertEqual(ttable.callTemplate('testPrint6', {'arg': '<&\"\'>'}),
                         '&lt;&amp;&quot;&#039;&gt;')
        

    def testComment(self):
        nameSpace = parseNamespace("""
        {namespace test}

        {template helloWorld1} //Hello world
           Hello world
        {/template}
    
        {template helloWorld2}
          /*Hello world*/
          Hello world
        {/template}""")

        ttable = makeTTable(nameSpace)

        self.assertEqual(ttable.callTemplate('helloWorld1', {}), 'Hello world')
        self.assertEqual(ttable.callTemplate('helloWorld2', {}), 'Hello world')

    def testCalculate(self):
        nameSpace = parseNamespace("""
        {namespace test}

        {template calculate1}{(2 + 3) * 4}{/template}
        
        {template calculate2}{(2 + 3) * 4}{/template}
        
        {template calculate3}
           {(20 - 3) %  5}
        {/template}
        
        {template calculate4}
           {hasData() ? 10 : 'Hello world'}
        {/template}
        
        {template calculate5}{randomInt(10)}{/template}
        
        {template calculate6}{$x + $y}{/template}

        {template calculate7}
           {not hasData() ? round(3.141592653589793) : round(2.7182817, $num)}
        {/template}

        {template calculate8}
           {$array[$index]}
        {/template}

        {template calculate9}
           {if $val == 5}true{else}false{/if}
        {/template}

        {template calculate10}{if $val != 5}true{else}false{/if}{/template}
        """)

        ttable = makeTTable(nameSpace)

        self.assertEqual(ttable.callTemplate('calculate1', {}), '20')
        self.assertEqual(ttable.callTemplate('calculate2', {}), '20')
        self.assertEqual(ttable.callTemplate('calculate3', {}), '2')
        
        self.assertEqual(ttable.callTemplate('calculate4', {}), 'Hello world')
        self.assertEqual(ttable.callTemplate('calculate4', {'a': 1}), '10')

        for i in xrange(100):
            r = int(ttable.callTemplate('calculate5', {}))
            self.assertGreaterEqual(r, 0)
            self.assertLess(r, 10)
        
        self.assertEqual(ttable.callTemplate('calculate6', {'x': 2, 'y': 3}), '5')
        self.assertEqual(ttable.callTemplate('calculate6', {'x': 'Hello ', 'y': 'world'}), 'Hello world')
        self.assertEqual(ttable.callTemplate('calculate6', {'x': 'Number: ', 'y': 6}), 'Number: 6')
        
        self.assertEqual(ttable.callTemplate('calculate7', {}), '3')
        self.assertEqual(ttable.callTemplate('calculate7', {'num': 2}), '2.72')
        self.assertEqual(ttable.callTemplate('calculate7', {'num': 4}), '2.7183')
        
        self.assertEqual(ttable.callTemplate('calculate8',
                                             { 'array': [0, 1, 4, 9, 16, 25, 36],
                                               'index': 1 }),
                         '1')
        self.assertEqual(ttable.callTemplate('calculate8',
                                             { 'array': [0, 1, 4, 9, 16, 25, 36],
                                               'index': 4 }),
                         '16')
        self.assertEqual(ttable.callTemplate('calculate8',
                                             { 'array': [0, 1, 4, 9, 16, 25, 36],
                                               'index': 3 }),
                         '9')
        self.assertEqual(ttable.callTemplate('calculate8',
                                             { 'array': [0, 1, 4, 9, 16, 25, 36],
                                               'index': 6 }),
                         '36')
                         
        self.assertEqual(ttable.callTemplate('calculate9', {'val': 6}), 'false')
        self.assertEqual(ttable.callTemplate('calculate9', {'val': 5}), 'true')

        self.assertEqual(ttable.callTemplate('calculate10', {'val': 6}), 'true')
        self.assertEqual(ttable.callTemplate('calculate10', {'val': 5}), 'false')

    def testSubstition(self):
        nameSpace = parseNamespace("""
        {namespace test}

        {template substitions}
            {sp}{nil}{\\r}{\\n}{\\t}{lb}{rb}
        {/template}
        """)

        ttable = makeTTable(nameSpace)

        self.assertEqual(ttable.callTemplate('substitions', {}), ' \r\n\t{}')

    def testDottedVariables(self):
        nameSpace = parseNamespace("""
        {namespace test}

        {template dotted1}
           {$obj.first} {$obj.second}
        {/template}

        {template dotted2}
           {$obj.msg.first}
           {$obj.msg.second}
        {/template}
        """)

        ttable = makeTTable(nameSpace)

        self.assertEqual(ttable.callTemplate('dotted1',
                                             {'obj': {'first': 'Hello', 'second': 'world'}}),
                         'Hello world')
        self.assertEqual(ttable.callTemplate('dotted2',
                                             {'obj': {'msg': {'first': 'Hello', 'second': 'world'}}}),
                         'Hello world')

    def testLocalVariables(self):
        nameSpace = parseNamespace("""
        {namespace test}

        {template local1}
            {foreach $b in $c}{$b.d}{/foreach}
        {/template}

        {template local2}
            {foreach $b in $c}{$b.d.a}{/foreach}
        {/template}
        """)

        ttable = makeTTable(nameSpace)

        self.assertEqual(ttable.callTemplate('local1',
                                             {'c': [{'d': 5}, {'d': 6}]}),
                         '56')
        self.assertEqual(ttable.callTemplate('local2',
                                             {'c': [{'d': {'a': 5}}, {'d': {'a': 6}}]}),
                         '56')

    def testLiteral(self):
        nameSpace = parseNamespace("""
        {namespace test}

        {template literal1}
            {literal}&{$x}{}{/literal}
        {/template}
        """)

        ttable = makeTTable(nameSpace)

        self.assertEqual(ttable.callTemplate('literal1', {}), '&{$x}{}')

    def testIf(self):
        nameSpace = parseNamespace("""
        {namespace test}

        {template testIf1}
            {if $name}Hello {$name}{/if}
        {/template}

        {template testIf2}
           Hello
           {if $name}{$name}{else}Guest{/if}
        {/template}

        {template testIf3}
            {if $hello}Hello {$hello}{elseif $by}By {$by}{elseif $thank}Thank {$thank}{else}Guest?{/if}
        {/template}
        """)

        ttable = makeTTable(nameSpace)

        self.assertEqual(ttable.callTemplate('testIf1', {'name': 'Andrey'}), 'Hello Andrey')
        self.assertEqual(ttable.callTemplate('testIf1', {}), '')

        self.assertEqual(ttable.callTemplate('testIf2', {'name': 'Andrey'}), 'Hello Andrey')
        self.assertEqual(ttable.callTemplate('testIf2', {}), 'Hello Guest')

        self.assertEqual(ttable.callTemplate('testIf3', {'hello': 'Andrey'}), 'Hello Andrey')
        self.assertEqual(ttable.callTemplate('testIf3', {'by': 'Masha'}), 'By Masha')
        self.assertEqual(ttable.callTemplate('testIf3', {'thank': 'Vasy'}), 'Thank Vasy')
        self.assertEqual(ttable.callTemplate('testIf3', {}), 'Guest?')

    def testSwitch(self):
        nameSpace = parseNamespace("""
        {namespace test}

        {template testSwitch1}
            {switch $var}{case 0}Variant 1: {$var}{case 1, 'Hello', 2}Variant 2: {$var}{default}Miss!{/switch}
        {/template}

        {template testSwitch2}
            {switch $var}{case 0}Variant 1: {$var}{case 1, 'Hello', 2}Variant 2: {$var}{/switch}
        {/template}
        """)

        ttable = makeTTable(nameSpace)

        self.assertEqual(ttable.callTemplate('testSwitch1', {'var': 0}), 'Variant 1: 0')
        self.assertEqual(ttable.callTemplate('testSwitch1', {'var': 'Hello'}), 'Variant 2: Hello')
        self.assertEqual(ttable.callTemplate('testSwitch1', {}), 'Miss!')
        self.assertEqual(ttable.callTemplate('testSwitch1', {'var': 2}), 'Variant 2: 2')

        self.assertEqual(ttable.callTemplate('testSwitch2', {'var': 0}), 'Variant 1: 0')
        self.assertEqual(ttable.callTemplate('testSwitch2', {'var': 'Hello'}), 'Variant 2: Hello')
        self.assertEqual(ttable.callTemplate('testSwitch2', {}), '')
        self.assertEqual(ttable.callTemplate('testSwitch2', {'var': 2}), 'Variant 2: 2')

    def testForeach(self):
        nameSpace = parseNamespace("""
        {namespace foreach}

        {template testForeach1}
            {foreach $opernand in $opernands}
                {sp}{$opernand}
            {/foreach}
        {/template}

        {template testForeach2}
            {foreach $opernand in $opernands}            
                {sp}{$opernand}
            {ifempty}
                Hello world
            {/foreach}
        {/template}

        {template testForeach3}
            {foreach $opernand in $opernands}
                {index($opernand)}
            {/foreach}
        {/template}

        {template testForeach4}
            {foreach $opernand in $opernands}
                {if not isFirst($opernand)}+{/if}{$opernand}
            {/foreach}
        {/template}

        {template testForeach5}
            {foreach $opernand in $opernands}
                {$opernand}{if not isLast($opernand)}+{/if}
            {/foreach}
        {/template}
        """)

        ttable = makeTTable(nameSpace)

        self.assertEqual(ttable.callTemplate('testForeach1',
                                             {'opernands': ["alpha", "beta", "gamma"]}),
                         ' alpha beta gamma')
        self.assertEqual(ttable.callTemplate('testForeach2',
                                             {'opernands': ["alpha", "beta", "gamma"]}),
                         ' alpha beta gamma')
        self.assertEqual(ttable.callTemplate('testForeach2',
                                             {}),
                         'Hello world')
        self.assertEqual(ttable.callTemplate('testForeach3', {'opernands': [1, 2, 3]}),
                         '123')
        self.assertEqual(ttable.callTemplate('testForeach4',
                                             {'opernands': ["alpha", "beta", "gamma"]}),
                         'alpha+beta+gamma')
        self.assertEqual(ttable.callTemplate('testForeach5',
                                             {'opernands': ["alpha", "beta", "gamma"]}),
                         'alpha+beta+gamma')

    def testFor(self):
        nameSpace = parseNamespace("""
        {namespace foreach}

        {template testFor1}
            {for $i in range(5)}{$i}{/for}
        {/template}

        {template testFor2}
            {for $i in range(4, 10)}{$i}{/for}
        {/template}

        {template testFor3}
            {for $i in range($from, $to, $by)}{$i}{/for}
        {/template}

        {template testFor4}
            {for $i in range(5, 8)}
                {for  $j in range(1, 3)}{$i}{$j}{/for}{sp}
            {/for}
        {/template}
        """)

        ttable = makeTTable(nameSpace)

        self.assertEqual(ttable.callTemplate('testFor1', {}), '01234')
        self.assertEqual(ttable.callTemplate('testFor2', {}), '456789')
        self.assertEqual(ttable.callTemplate('testFor3', {'from': 1, 'to': 10, 'by': 3}), '147')
        self.assertEqual(ttable.callTemplate('testFor4', {}), '5152 6162 7172 ')

    def testCall(self):
        nameSpace = parseNamespace("""
        {namespace call}

        {template helloWorld}
            Hello world
        {/template}

        {template helloName}
            Hello {$name}
        {/template}

        {template helloName2}
            Hello {$name} from {$city}
        {/template}

        {template testCall1}
            {call helloWorld /}
        {/template}

        {template testCall2}
            {call helloName}
                {param name: 'Andrey'/}
            {/call}
        {/template}

        {template testCall3}
            {call helloName}
                {param name}Andrey{/param}
            {/call}
        {/template}

        {template testCall4}
           {call helloName data=\"all\"/}
        {/template}

        {template testCall5}
            {call helloName}
                {param name}
                    {call helloName data=\"all\"/}
                {/param}
            {/call}
        {/template}

        {template testCall6}
            {call helloName data=\"$author\"/}
        {/template}

        {template testCall7}
            {call helloName2 data=\"$author\"}
                {param name: 'Andrey' /}
            {/call}
        {/template}

        {template testCall8}
            {call name=\"'hello' + 'World'\" /}
        {/template}
        """)

        ttable = makeTTable(nameSpace)

        self.assertEqual(ttable.callTemplate('testCall1', {}), 'Hello world')
        self.assertEqual(ttable.callTemplate('testCall2', {}), 'Hello Andrey')
        self.assertEqual(ttable.callTemplate('testCall3', {}), 'Hello Andrey')
        self.assertEqual(ttable.callTemplate('testCall4', {'name': 'Masha'}), 'Hello Masha')
        self.assertEqual(ttable.callTemplate('testCall5', {'name': 'Ivan'}), 'Hello Hello Ivan')
        self.assertEqual(ttable.callTemplate('testCall6', {'author': {'name': 'Masha'}}), 'Hello Masha')
        self.assertEqual(ttable.callTemplate('testCall7',
                                             {'author': {'name': 'Masha', 'city': 'Krasnodar'}}),
                         'Hello Andrey from Krasnodar')
        self.assertEqual(ttable.callTemplate('testCall8', {}), 'Hello world')
        

if __name__ == "__main__":
    unittest.main()

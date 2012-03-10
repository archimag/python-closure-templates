//

var ClosureTemplate = {  };

ClosureTemplate.Test = {  };

// Simple

ClosureTemplate.Test.testSimple = function () {
    this.assertEqual('Hello world!', closureTemplate.python.testSimple1());
    this.assertEqual('<Hello world>', closureTemplate.python.testSimple2());
};

// Print

ClosureTemplate.Test.testPrint = function () {
    this.assertEqual('&lt;&amp;&quot;&#039;&gt;',
                     closureTemplate.python.testPrint1({arg: '<&\"\'>'}));  
    this.assertEqual('<&\"\'>',
                     closureTemplate.python.testPrint2({arg: '<&\"\'>'}));  
    this.assertEqual('<&\"\'>',
                     closureTemplate.python.testPrint3({arg: '<&\"\'>'}));  
    this.assertEqual('~!@#$%25%5E&*()%7B%7D%5B%5D=:/,;?+\'%22%5C',
                     closureTemplate.python.testPrint4({arg: '~!@#$%^&*(){}[]=:/,;?+\'\"\\'}));  
    this.assertEqual('~!%40%23%24%25%5E%26*()%7B%7D%5B%5D%3D%3A%2F%2C%3B%3F%2B\'%22%5C',
                     closureTemplate.python.testPrint5({arg: '~!@#$%^&*(){}[]=:/,;?+\'\"\\'}));  
    this.assertEqual('&lt;&amp;&quot;&#039;&gt;',
                     closureTemplate.python.testPrint6({arg: '<&\"\'>'}));
};

// Comment

ClosureTemplate.Test.testComment = function () {
    this.assertEqual('Hello world',
                     closureTemplate.python.testComment1());
    this.assertEqual('Hello world',
                     closureTemplate.python.testComment2());
};

// Calculate

ClosureTemplate.Test.testCalculate = function () {
    this.assertEqual('20',
                     closureTemplate.python.testCalculate1());
    this.assertEqual('20',
                     closureTemplate.python.testCalculate2());
    this.assertEqual('2',
                     closureTemplate.python.testCalculate3());

    this.assertEqual('Hello world',
                     closureTemplate.python.testCalculate4());
    this.assertEqual('10',
                     closureTemplate.python.testCalculate4({a: 1}));


    this.assertEqual('5',
                     closureTemplate.python.testCalculate6({ x: 2, y: 3 }));
    this.assertEqual('Hello world',
                     closureTemplate.python.testCalculate6({ x: 'Hello ', y: 'world' }));
    this.assertEqual('Number: 6',
                     closureTemplate.python.testCalculate6({ x: 'Number: ', y: 6 }));


    this.assertEqual('3',
                     closureTemplate.python.testCalculate7());
    this.assertEqual('3',
                     closureTemplate.python.testCalculate7({}));
    this.assertEqual('2.72',
                     closureTemplate.python.testCalculate7({ num: 2 }));
    this.assertEqual('2.7183',
                     closureTemplate.python.testCalculate7({ num: 4 }));

    this.assertEqual('1',
                     closureTemplate.python.testCalculate8({ array: [0, 1, 4, 9, 16, 25, 36],
                                                             index: 1 }));
    this.assertEqual('16',
                     closureTemplate.python.testCalculate8({ array: [0, 1, 4, 9, 16, 25, 36],
                                                             index: 4 }));
    this.assertEqual('9',
                     closureTemplate.python.testCalculate8({ array: [0, 1, 4, 9, 16, 25, 36],
                                                             index: 3 }));
    this.assertEqual('36',
                     closureTemplate.python.testCalculate8({ array: [0, 1, 4, 9, 16, 25, 36],
                                                             index: 6 }));

    this.assertEqual('false',
                     closureTemplate.python.testCalculate9({ val: 6 }));
    this.assertEqual('true',
                     closureTemplate.python.testCalculate9({ val: 5 }));

    this.assertEqual('true',
                     closureTemplate.python.testCalculate10({ val: 6 }));
    this.assertEqual('false',
                     closureTemplate.python.testCalculate10({ val: 5 }));
};

// Random

ClosureTemplate.Test.testRandom = function () {
    for (var i = 0; i < 100; ++i) {
        var rnd = parseInt(closureTemplate.python.testCalculate5());

        
        this.assert(rnd >= 0);
        this.assert(rnd < 10);
    }
};


// Substitions

ClosureTemplate.Test.testSubstition = function () {
    this.assertEqual(' \r\n\t{}',
                     closureTemplate.python.testSubstitions());
};

// Dotted

ClosureTemplate.Test.testDottedVariables = function () {
    this.assertEqual('Hello world',
                     closureTemplate.python.testDotted1({ obj: { first: 'Hello', second: 'world' } }));
    this.assertEqual('Hello world',
                     closureTemplate.python.testDotted2({ obj: { msg: { first: 'Hello', second: 'world' } } }));
};

// Local variables

ClosureTemplate.Test.testLocalVariables = function () {
    this.assertEqual('56',
                     closureTemplate.python.testLocal1({ c: [{ d: 5 }, { d: 6}]}));
    this.assertEqual('56',
                     closureTemplate.python.testLocal2({ c: [{ d: { a: 5 } }, { d: { a: 6 } }] }));

};

// Literals

ClosureTemplate.Test.testLiteral = function () {
    this.assertEqual('\'"&{$x}{}',
                     closureTemplate.python.testLiteral1());
};

// If

ClosureTemplate.Test.testIf = function () {
    this.assertEqual('Hello Andrey',
                     closureTemplate.python.testIf1({ name: 'Andrey' }));
    this.assertEqual('',
                     closureTemplate.python.testIf1());

    this.assertEqual('Hello Andrey',
                     closureTemplate.python.testIf2({ name: 'Andrey' }));
    this.assertEqual('Hello Guest',
                     closureTemplate.python.testIf2({}));


    this.assertEqual('Hello Andrey',
                     closureTemplate.python.testIf3({ hello: 'Andrey' }));
    this.assertEqual('By Masha',
                     closureTemplate.python.testIf3({ by: 'Masha' }));
    this.assertEqual('Thank Vasy',
                     closureTemplate.python.testIf3( { thank: 'Vasy' }));
    this.assertEqual('Guest?',
                     closureTemplate.python.testIf3({}));
};

// Switch

ClosureTemplate.Test.testSwitch = function () {
    this.assertEqual('Variant 1: 0',
                    closureTemplate.python.testSwitch1({ 'var': 0 }));
    this.assertEqual('Variant 2: Hello',
                    closureTemplate.python.testSwitch1({ 'var': 'Hello' }));
    this.assertEqual('Miss!',
                    closureTemplate.python.testSwitch1());
    this.assertEqual('Variant 2: 2',
                    closureTemplate.python.testSwitch1({ 'var': 2 }));

    this.assertEqual('Variant 1: 0',
                    closureTemplate.python.testSwitch2({ 'var': 0 }));
    this.assertEqual('Variant 2: Hello',
                    closureTemplate.python.testSwitch2({ 'var': 'Hello' }));
    this.assertEqual('',
                    closureTemplate.python.testSwitch2({}));
    this.assertEqual('Variant 2: 2',
                    closureTemplate.python.testSwitch2({ 'var': 2 }));

};

// Foreach

ClosureTemplate.Test.testForeach = function () {
    this.assertEqual(' alpha beta gamma',
                     closureTemplate.python.testForeach1({ opernands: ["alpha", "beta", "gamma"] }));
    this.assertEqual(' alpha beta gamma',
                     closureTemplate.python.testForeach2({ opernands: ["alpha", "beta", "gamma"] }));
    this.assertEqual('Hello world',
                     closureTemplate.python.testForeach2({}));
    this.assertEqual('123',
                     closureTemplate.python.testForeach3({ opernands: [1, 2, 3] }));
    this.assertEqual('alpha+beta+gamma',
                     closureTemplate.python.testForeach4({ opernands: ["alpha", "beta", "gamma"] }));
    this.assertEqual('alpha+beta+gamma',
                     closureTemplate.python.testForeach5({ opernands: ["alpha", "beta", "gamma"] }));
};

// For

ClosureTemplate.Test.testFor = function () {
    this.assertEqual('01234',
                    closureTemplate.python.testFor1());
    this.assertEqual('456789',
                    closureTemplate.python.testFor2());
    this.assertEqual('147',
                    closureTemplate.python.testFor3({ from: 1, to: 10, by: 3 }));
    this.assertEqual('5152 6162 7172 ',
                     closureTemplate.python.testFor4({}));
};

// Call

ClosureTemplate.Test.testCall = function () {
    this.assertEqual('Hello world',
                    closureTemplate.python.testCall1());
    this.assertEqual('Hello Andrey',
                    closureTemplate.python.testCall2());
    this.assertEqual('Hello Andrey',
                    closureTemplate.python.testCall3());
    this.assertEqual('Hello Masha',
                    closureTemplate.python.testCall4({ name: 'Masha' }));
    this.assertEqual('Hello Hello Ivan',
                    closureTemplate.python.testCall5({'name': 'Ivan'}));
    this.assertEqual('Hello Masha',
                    closureTemplate.python.testCall6({author: {'name': 'Masha'}}));
    this.assertEqual('Hello Andrey from Krasnodar',
                    closureTemplate.python.testCall7({'author': {name: 'Masha', city: 'Krasnodar'}}));
    this.assertEqual('Hello world',
                    closureTemplate.python.testCall8());
    this.assertEqual('Hello Andrey',
                    closureTemplate.python.testCall9());

};
import os
import sys

import pyparsing as pp
from pyparsing import pyparsing_common as ppc

Lit = pp.Literal
Opt = pp.Optional
Sup = pp.Suppress
Fwd = pp.Forward
DList = pp.DelimitedList

LPAREN, RPAREN, LBRACE, RBRACE, SEMI, COMMA = map(Sup, map(Lit, '(){};,'))

name = ppc.identifier('name')
value = ppc.number | pp.quoted_string
pp.quoted_string.add_parse_action(pp.remove_quotes)
args = DList(value)
definition = name + LPAREN + pp.ZeroOrMore(args)('args') + RPAREN
property_def = pp.Group(definition + SEMI)
instance = Fwd()
object_body = pp.Group(instance[1, ...])('body')
object_def = pp.Group(definition + LBRACE + Opt(object_body) + RBRACE)
instance <<= (property_def | object_def)
config_doc = instance[0, ...]


def parse_config_file(file):
    with open(file, 'r') as f:
        return config_doc.parse_string(f.read(), parse_all=True)


if __name__ == '__main__':
    name_tests = [
        'Path',
        'Properties',
    ]

    value_tests = [
        '0',
        '1',
        '-1',
        '1.0001',
        '-0.2001',
        '1E5',
        '"Hermite"',
        '"Hello, world!"',
    ]

    args_tests = [
        '7',
        '7,1.0',
        '7, 1.0',
    ]

    definition_tests = [
        'Property()',
        'Property(1)',
        'Property(-2)',
        'Property(3.14)',
        'Property(1, 2.0)',
        'Property(2.0, "Things")'
    ]

    object_def_tests = [
        '''Scoped(){}''',
        '''Scoped(1){}''',
        '''Scoped(){
        Inside();
        }''',
        '''Scoped(){
        Inside() {}
        }''',
        '''Scoped() {
        Inside() {
        MoreInside() {}
        }
        AgainInside() {
        Something(1, 2, 3);
        }
        }''',
    ]

    config_doc_tests = [
        '',
        '''
Version(10);
PathCount(4);

Path("cp4_spawn")
{
    Data(0);
    PathType(0);
    PathSpeedType(0);
    PathTime(0.000000);
    OffsetPath(0);
    Layer(1);
    SplineType("Hermite");
    
    Properties(0)
    {
    }
    
    Nodes(1)
    {
        Node()
        {
            Position(-131.019501, 0.000000, -251.667999);
            Properties(0)
            {
            }
        }
    }
}
Path("cp3_spawn")
{
    Data(0);
    PathType(0);
    PathSpeedType(0);
    PathTime(0.000000);
    OffsetPath(0);
    Layer(1);
    SplineType("Hermite");
    
    Properties(0)
    {
    }
    
    Nodes(1)
    {
        Node()
        {
            Position(-141.019501, 0.000000, -241.667999);
            Properties(0)
            {
            }
        }
    }
}
''',
    ]

    with open(os.devnull, 'w') as f:
        failed = not all([x[0] for x in [
            name.run_tests(name_tests, file=f),
            value.run_tests(value_tests, file=f),
            args.run_tests(args_tests, file=f),
            definition.run_tests(definition_tests, file=f),
            property_def.run_tests([s + ';' for s in definition_tests], file=f),
            object_def.run_tests(object_def_tests, file=f),
            config_doc.run_tests(config_doc_tests, file=f),
        ]])
        if failed:
            print('Fail')
            sys.exit(1)
        else:
            print('Pass')

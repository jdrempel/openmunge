import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from mungers.ast.Args import FloatArg, StrArg
from mungers.ast.Config import Config
from mungers.ast.ConfigInstance import ConfigInstance

Lit = pp.Literal
Opt = pp.Optional
Sup = pp.Suppress
Fwd = pp.Forward
DList = pp.DelimitedList

LPAREN, RPAREN, LBRACE, RBRACE, SEMI, COMMA = map(Sup, map(Lit, '(){};,'))

name = ppc.identifier('name')
value = ppc.fnumber.add_parse_action(FloatArg.build) | pp.quoted_string.add_parse_action(pp.remove_quotes, StrArg.build)
args = DList(value)
definition = name + LPAREN + pp.ZeroOrMore(args)('args') + RPAREN
property_def = pp.Group(definition + SEMI)
instance = Fwd()
object_body = instance[1, ...]('body')
object_def = pp.Group(definition + LBRACE + Opt(object_body) + RBRACE)
instance <<= (property_def.set_parse_action(ConfigInstance.build_property) |
              object_def.set_parse_action(ConfigInstance.build_instance))


def parse_config_file(file, doc_cls=Config):
    config_doc = instance[...].set_parse_action(doc_cls.build)
    with open(file, 'r') as f:
        return config_doc.parse_string(f.read(), parse_all=True)[0]

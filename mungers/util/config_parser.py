import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from mungers.ast.Args import FloatArg, StrArg
from mungers.ast.Config import Config
from mungers.ast.ConfigInstance import ConfigInstance
from mungers.ast.Object import Object
from mungers.ast.Property import Property

Lit = pp.Literal
Opt = pp.Optional
Sup = pp.Suppress
Fwd = pp.Forward
Key = pp.Keyword
DList = pp.DelimitedList

LPAREN, RPAREN, LBRACE, RBRACE, SEMI, COMMA = map(Sup, map(Lit, '(){};,'))
specials = (
    ('Animation', Object),  # TODO
    ('Barrier', Object),  # TODO
    ('Hint', Object),  # TODO
    ('Object', Object),
)
special_keys = pp.MatchFirst([Key(s[0]) for s in specials])

args = Fwd()
property_def = Fwd()

object_signature = Key('Object')('name') + LPAREN + pp.ZeroOrMore(args)('args') + RPAREN
object_body = property_def[1, ...]('body')
object_def = pp.Group(object_signature + LBRACE + Opt(object_body) + RBRACE)

name = ~special_keys + ppc.identifier('name')
value = ppc.fnumber.add_parse_action(FloatArg.build) | pp.quoted_string.add_parse_action(pp.remove_quotes, StrArg.build)
args <<= DList(value)
property_signature = name + LPAREN + pp.ZeroOrMore(args)('args') + RPAREN
property_def <<= pp.Group(property_signature + SEMI)
property_ = Fwd()
scope_body = property_[1, ...]('body')
scoped_def = pp.Group(property_signature + LBRACE + Opt(scope_body) + RBRACE)
property_ <<= (property_def.set_parse_action(ConfigInstance.build_property) |
               scoped_def.set_parse_action(ConfigInstance.build_instance))


doc_entry = object_def.set_parse_action(Object.build) | property_


def parse_config_file(file, doc_cls=Config):
    config_doc = doc_entry[...].set_parse_action(doc_cls.build)
    with open(file, 'r') as f:
        return config_doc.parse_string(f.read(), parse_all=True)[0]

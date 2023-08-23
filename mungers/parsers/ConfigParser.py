import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from mungers.ast.Args import FloatArg, NumberArgFactory, StrArg
from mungers.ast.Barrier import Barrier
from mungers.ast.ConfigInstance import ConfigInstance
from mungers.ast.Hint import Hint
from mungers.ast.InstProperty import InstProperty
from mungers.ast.Object import Object
from mungers.ast.Region import Region
from mungers.parsers.ParserOptions import ParserOptions


class ConfigParser:
    def __init__(self, options: ParserOptions):
        LPAREN, RPAREN, LBRACE, RBRACE, SEMI, COMMA = map(pp.Suppress, map(pp.Literal, '(){};,'))
        specials = ('Animation', 'Barrier', 'Hint', 'Object', 'Region')
        special_keys = pp.MatchFirst([pp.Keyword(s) for s in specials])

        self.args = pp.Forward()
        self.property_signature = pp.Forward()

        property_def = pp.Group(self.property_signature + SEMI).set_parse_action(InstProperty.build)

        object_signature = pp.Keyword('Object')('name') + LPAREN + pp.ZeroOrMore(self.args)('args') + RPAREN
        object_body = property_def[1, ...]('body')
        self.object_def = pp.Group(object_signature + LBRACE + pp.Optional(object_body) + RBRACE)

        region_signature = pp.Keyword('Region')('name') + LPAREN + pp.ZeroOrMore(self.args)('args') + RPAREN
        region_body = property_def[1, ...]('body')
        self.region_def = pp.Group(region_signature + LBRACE + pp.Optional(region_body) + RBRACE)

        hint_signature = pp.Keyword('Hint')('name') + LPAREN + pp.ZeroOrMore(self.args)('args') + RPAREN
        hint_body = property_def[1, ...]('body')
        self.hint_def = pp.Group(hint_signature + LBRACE + pp.Optional(hint_body) + RBRACE)

        barrier_signature = pp.Keyword('Barrier')('name') + LPAREN + pp.ZeroOrMore(self.args)('args') + RPAREN
        barrier_body = property_def[1, ...]('body')
        self.barrier_def = pp.Group(barrier_signature + LBRACE + pp.Optional(barrier_body) + RBRACE)

        self.name = ~special_keys + ppc.identifier('name')
        if options.all_values_are_strings:
            self.value = (ppc.number.add_parse_action(StrArg.build) |
                          pp.quoted_string.set_parse_action(pp.remove_quotes, StrArg.build))
        elif options.all_numbers_are_floats:
            self.value = (ppc.fnumber.add_parse_action(FloatArg.build) |
                          pp.quoted_string.set_parse_action(pp.remove_quotes, StrArg.build))
        else:
            self.value = (ppc.number.add_parse_action(NumberArgFactory.build) |
                          pp.quoted_string.set_parse_action(pp.remove_quotes, StrArg.build))
        self.args <<= pp.DelimitedList(self.value)
        self.property_signature <<= self.name + LPAREN + pp.ZeroOrMore(self.args)('args') + RPAREN
        instance_def = pp.Group(self.property_signature + SEMI)
        self.property_ = pp.Forward()
        scope_body = self.property_[1, ...]('body')
        scoped_def = pp.Group(self.property_signature + LBRACE + pp.Optional(scope_body) + RBRACE)
        self.property_ <<= (instance_def.set_parse_action(ConfigInstance.build_property) |
                            scoped_def.set_parse_action(ConfigInstance.build_instance))

        self.document = (self.object_def.set_parse_action(Object.build) |
                         self.region_def.set_parse_action(Region.build) |
                         self.hint_def.set_parse_action(Hint.build) |
                         self.barrier_def.set_parse_action(Barrier.build) |
                         self.property_)
        self.document_cls = options.document_cls

    def parse_file(self, file):
        config_doc = self.document[...].set_parse_action(self.document_cls.build)
        with open(file, 'r') as f:
            return config_doc.parse_string(f.read(), parse_all=True)[0]

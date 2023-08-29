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
        lparen, rparen, lbrace, rbrace, semi, comma = map(pp.Suppress, map(pp.Literal, '(){};,'))
        specials = ('Animation', 'Barrier', 'Hint', 'Object', 'Region')
        special_keys = pp.MatchFirst([pp.Keyword(s) for s in specials])

        self.args = pp.Forward()
        self.property_signature = pp.Forward()

        property_def = pp.Group(self.property_signature + semi).set_parse_action(InstProperty.build)

        object_signature = pp.Keyword('Object')('name') + lparen + pp.ZeroOrMore(self.args)('args') + rparen
        object_body = property_def[1, ...]('body')
        self.object_def = pp.Group(object_signature + lbrace + pp.Optional(object_body) + rbrace)

        region_signature = pp.Keyword('Region')('name') + lparen + pp.ZeroOrMore(self.args)('args') + rparen
        region_body = property_def[1, ...]('body')
        self.region_def = pp.Group(region_signature + lbrace + pp.Optional(region_body) + rbrace)

        hint_signature = pp.Keyword('Hint')('name') + lparen + pp.ZeroOrMore(self.args)('args') + rparen
        hint_body = property_def[1, ...]('body')
        self.hint_def = pp.Group(hint_signature + lbrace + pp.Optional(hint_body) + rbrace)

        barrier_signature = pp.Keyword('Barrier')('name') + lparen + pp.ZeroOrMore(self.args)('args') + rparen
        barrier_body = property_def[1, ...]('body')
        self.barrier_def = pp.Group(barrier_signature + lbrace + pp.Optional(barrier_body) + rbrace)

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
        self.property_signature <<= self.name + lparen + pp.ZeroOrMore(self.args)('args') + rparen
        instance_def = pp.Group(self.property_signature + semi)
        self.property_ = pp.Forward()
        scope_body = self.property_[1, ...]('body')
        scoped_def = pp.Group(self.property_signature + lbrace + pp.Optional(scope_body) + rbrace)
        self.property_ <<= (instance_def.set_parse_action(ConfigInstance.build_property) |
                            scoped_def.set_parse_action(ConfigInstance.build_instance))

        self.document = (self.object_def.set_parse_action(Object.build) |
                         self.region_def.set_parse_action(Region.build) |
                         self.hint_def.set_parse_action(Hint.build) |
                         self.barrier_def.set_parse_action(Barrier.build) |
                         self.property_)
        self.document_cls = options.document_cls

    # noinspection PyUnresolvedReferences
    def parse_file(self, file):
        config_doc = self.document[...].set_parse_action(self.document_cls.build)
        with open(file, 'r') as f:
            return config_doc.parse_string(f.read(), parse_all=True)[0]

import pyparsing as pp

from mungers.ast.ReqList import ReqList

Lit = pp.Literal
Opt = pp.Optional
Sup = pp.Suppress
Fwd = pp.Forward
Key = pp.Keyword

LBRACE, RBRACE = map(Sup, map(Lit, '{}'))
UCFT, REQN = map(Sup, map(Key, ('ucft', 'REQN')))

pp.dbl_quoted_string.add_parse_action(pp.remove_quotes)

header = pp.dbl_quoted_string
# TODO there is an optional sub-header which has the format "platform=<PC|PS2|XBOX>"
entry = pp.dbl_quoted_string
entries = (header.set_results_name('header') +
           pp.Group(entry[0, ...], aslist=True).set_results_name('entries').set_parse_action(list))
section = (REQN + LBRACE + entries + RBRACE).set_parse_action(ReqList.build)
req_doc = UCFT + LBRACE + section[0, ...] + RBRACE


def parse_req_file(file):
    with open(file, 'r') as f:
        return req_doc.parse_string(f.read(), parse_all=True).as_list()

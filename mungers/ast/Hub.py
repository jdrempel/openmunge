from collections import defaultdict

from core.types.math import Vector3
from core.util.hashing import magic
from mungers.chunks.Chunk import Chunk

HUB_MAX_ARCS = 8
HUB_NAME_SIZE = 16
NUM_TYPES = 5


class Hub:
    def __init__(self):
        self.name = None
        self.hub_name = None
        self.position = Vector3()
        self.radius = 0.0

        self.outgoing_connections = dict()  # connection: destination hub
        self.incoming_connections = dict()  # connection: origin hub
        self.type_connections = dict()  # type_: list of connections
        self.has_types = []  # list of bools

    def __str__(self):
        return 'Hub({})'.format(self.hub_name)

    @staticmethod
    def build(tok):
        inst = Hub()
        inst.name = tok[0].name
        inst.hub_name = str(tok[0].args[0])
        body = tok[0].body.as_list() or []
        for x in body:
            if x.name == magic('Pos'):
                inst.position = Vector3(*[float(arg) for arg in x.args])
                inst.position.z *= -1
            elif x.name == magic('Radius'):
                inst.radius = float(x.args[0])
        return inst

    def to_binary(self, parent: Chunk, plan_doc):
        parent.write_str_fixed(self.hub_name, HUB_NAME_SIZE)

        for f in self.position.flatten():
            parent.write_float(f)

        parent.write_float(self.radius)

        for index in range(HUB_MAX_ARCS):
            if index >= len(plan_doc.hub_connection_index_map[self.hub_name]):
                parent.write_byte(0xFF)
                continue
            parent.write_byte(plan_doc.hub_connection_index_map[self.hub_name][index])

        types_on_hub = []

        for i in range(NUM_TYPES):
            type_is_on_hub = self.has_arc_type(plan_doc, i)
            types_on_hub.append(type_is_on_hub)
            parent.write_byte(int(type_is_on_hub))

        for i, filter_type in enumerate(types_on_hub):
            if not filter_type:
                continue
            connected_compatible_arcs = self.get_hub_connections_with_type_or_lower(plan_doc, i)
            connected_hubs = {plan_doc.name_hub_map[arc.get_hub_opposite_name(self)]: arc
                              for arc in connected_compatible_arcs}
            global_hub_count_map = defaultdict(int)
            # Look for outbound connections with compatible type
            for other_hub in plan_doc.hubs:
                if other_hub is self:
                    parent.write_byte(0)
                    continue
                if other_hub not in connected_hubs:
                    if other_hub.has_arc_type(plan_doc, i):
                        parent.write_byte(0xF8)
                    else:
                        parent.write_byte(0)
                    continue
                # Need to check if other hub has a higher (only?) arc type and if not, write 0
                if connected_hubs[other_hub].flag < 2**i:
                    parent.write_byte(0)
                    continue
                if connected_hubs[other_hub].one_way and connected_hubs[other_hub].start_hub != self.hub_name:
                    # Connected, but it's one-way, and it points into this hub
                    parent.write_byte(0)
                    continue
                outbound_arc_index = plan_doc.connections.index(connected_hubs[other_hub])
                for inbound_arc_index, maybe_inbound_arc in enumerate(plan_doc.connections):
                    if maybe_inbound_arc.start_hub != self.hub_name != maybe_inbound_arc.end_hub:
                        # Not connected to this hub
                        continue
                    if inbound_arc_index >= outbound_arc_index:
                        # Only increment the count if the inbound index is less than the outbound
                        continue
                    if maybe_inbound_arc.has_type_or_higher(i):
                        global_hub_count_map[other_hub] += 1

                parent.write_byte(0xF8 | (global_hub_count_map[other_hub] & 0x7))

    def has_arc_type(self, context, type_index):
        return any(arc.has_type(type_index) for arc in context.hub_connection_map[self.hub_name])

    def get_hub_connections_with_type(self, context, type_index: int) -> list:
        return [arc for arc in context.hub_connection_map[self.hub_name] if arc.has_type(type_index)]

    def get_hub_connections_with_type_or_lower(self, context, max_type_index: int) -> list:
        return [arc for arc in context.hub_connection_map[self.hub_name] if arc.has_type_or_lower(max_type_index)]

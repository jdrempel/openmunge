from collections import defaultdict

from mungers.ast.Connection import Connection
from mungers.ast.Hub import Hub
from mungers.chunks.Chunk import Chunk

NUM_TYPES = 5


class PlanningDoc(Chunk):
    def __init__(self):
        super().__init__('plan')

        self.hubs = []
        self.connections = []
        self.types = [False]*NUM_TYPES

        self.name_hub_map = dict()
        self.hub_connection_index_map = defaultdict(list)
        self.hub_connection_map = defaultdict(list)

    def __repr__(self):
        return 'PlanningDoc[{},{}]'.format(len(self.hubs), len(self.connections))

    @property
    def id(self):
        return 'plan'

    @staticmethod
    def build(tok):
        plan = PlanningDoc()
        instances = tok.as_list()

        def get_hub_index(name: str) -> int:
            for i, hub in enumerate(plan.hubs):
                if hub.hub_name == name:
                    return i
            return -1

        for instance in instances:
            if isinstance(instance, Hub):
                plan.hubs.append(instance)
                plan.name_hub_map[instance.hub_name] = instance
            elif isinstance(instance, Connection):
                start = instance.start_hub
                end = instance.end_hub
                start_hub = plan.name_hub_map[start]
                end_hub = plan.name_hub_map[end]

                start_hub.outgoing_connections[instance] = end_hub
                end_hub.incoming_connections[instance] = start_hub
                if not instance.one_way:
                    start_hub.incoming_connections[instance] = end_hub
                    end_hub.outgoing_connections[instance] = start_hub

                for x in range(NUM_TYPES):
                    if not instance.flag & int(2**x):
                        continue
                    start_hub.type_connections[x] = instance
                    end_hub.type_connections[x] = instance

                plan.hub_connection_index_map[start].append(len(plan.connections))
                plan.hub_connection_index_map[end].append(len(plan.connections))
                plan.hub_connection_map[start].append(instance)
                plan.hub_connection_map[end].append(instance)

                instance.endpoints = [get_hub_index(start), get_hub_index(end)]
                plan.connections.append(instance)

                types = [bool(instance.flag & int(2**x)) for x in range(NUM_TYPES)]
                for i, type_ in enumerate(types):
                    plan.types[i] |= type_

        return plan

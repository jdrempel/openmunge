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
            for h, hub in enumerate(plan.hubs):
                if hub.hub_name == name:
                    return h
            return -1

        for instance in instances:
            if isinstance(instance, Hub):
                plan.hubs.append(instance)
                plan.name_hub_map[instance.hub_name] = instance
            elif isinstance(instance, Connection):
                start = instance.start_hub
                end = instance.end_hub

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

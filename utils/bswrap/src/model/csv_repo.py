import csv
from pathlib import Path
from .models import Result
from .iface import IResultRepo


class CSVResultRepo(IResultRepo):
    _headers = [
        "topo_name",
        "topo_num_nodes",
        "topo_links",
        "cfg_routing_func",
        "cfg_traffic_type",
        "cfg_sim_count",
        "packet_latency_min",
        "packet_latency_max",
        "packet_latency_avg",
        "network_latency_min",
        "network_latency_max",
        "network_latency_avg",
        "flit_latency_min",
        "flit_latency_max",
        "flit_latency_avg",
        "fragmentation_min",
        "fragmentation_max",
        "fragmentation_avg",
        "injected_packet_rate_min",
        "injected_packet_rate_max",
        "injected_packet_rate_avg",
        "accepted_packet_rate_min",
        "accepted_packet_rate_max",
        "accepted_packet_rate_avg",
        "injected_flit_rate_min",
        "injected_flit_rate_max",
        "injected_flit_rate_avg",
        "accepted_flit_rate_min",
        "accepted_flit_rate_max",
        "accepted_flit_rate_avg",
        "injected_packet_size_avg",
        "accepted_packet_size_avg",
        "hops_avg",
    ]

    def __init__(self, file: Path):
        self._savefile = file
        self._header_printed = False

    def save(self, obj: Result) -> None:
        if not isinstance(obj, Result):
            raise ValueError("Supplied object must be "
                             "instance of Result class")
        with open(self._savefile, "a") as file:
            writer = csv.DictWriter(file, self._headers)
            if not self._header_printed:
                self._header_printed = True
                writer.writeheader()
            writer.writerow(obj.to_dict())

    def close(self) -> None:
        pass

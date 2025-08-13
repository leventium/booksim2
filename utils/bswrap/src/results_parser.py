import io
import os
import re
from dataclasses import dataclass
from tqdm import tqdm
import matplotlib.pyplot as plt


@dataclass
class FeatureRange:
    min: float
    max: float
    avg: float


@dataclass
class SimResult:
    packet_lat: FeatureRange
    network_lat: FeatureRange
    flit_lat: FeatureRange
    fragmentation: FeatureRange
    injected_packet_rate: FeatureRange
    accepted_packet_rate: FeatureRange
    injected_flit_rate: FeatureRange
    accepted_flit_rate: FeatureRange
    injected_packet_size_avg: float
    accepted_packet_size_avg: float
    hops_avg: float


class BadSimSummary(Exception):
    pass


class SimSummaryNotFound(Exception):
    pass


FEATURE_RE = re.compile(r"\.*= ([+-]?\d+(\.\d+(e[+-]?\d+)?)?)")
FILENAME_RE = re.compile(r"result_(\w+)_F(\w+)_T(\w+)_S(\d+)")


def get_float_from_line(line: str) -> float:
    return float(FEATURE_RE.search(line)[1])


def parse_feature(file: io.StringIO) -> FeatureRange:
    try:
        return FeatureRange(
            avg=get_float_from_line(file.readline()),
            min=get_float_from_line(file.readline()),
            max=get_float_from_line(file.readline()),
        )
    except ValueError:
        raise BadSimSummary("Error while parsing feature")


def parse_file(file: io.StringIO) -> SimResult:
    line = file.readline()
    while line != "" and line != "====== Traffic class 0 ======\n":
        line = file.readline()
    if line == "":
        raise SimSummaryNotFound("Sim summary wasn't found in this file")
    try:
        res = SimResult(
            packet_lat=parse_feature(file),
            network_lat=parse_feature(file),
            flit_lat=parse_feature(file),
            fragmentation=parse_feature(file),
            injected_packet_rate=parse_feature(file),
            accepted_packet_rate=parse_feature(file),
            injected_flit_rate=parse_feature(file),
            accepted_flit_rate=parse_feature(file),
            injected_packet_size_avg=get_float_from_line(file.readline()),
            accepted_packet_size_avg=get_float_from_line(file.readline()),
            hops_avg=get_float_from_line(file.readline()),
        )
    except ValueError:
        raise BadSimSummary("Error while parsing solid features")
    return res


@dataclass
class CirculantTopo:
    num_nodes: int
    links: list[int]

    def __eq__(self, value):
        if type(value) != CirculantTopo:
            return False
        return self.links == value.links

    def get_topo_name(self) -> str:
        res = f"C({"N" if self.num_nodes == 0 else self.num_nodes};"
        for i in range(len(self.links)):
            res += str(self.links[i])
            if i != len(self.links) - 1:
                res += ","
        res += ")"
        return res
    
    def get_num_nodes(self):
        return self.num_nodes


@dataclass
class MeshTopo:
    radix: int
    ndim: int

    def __eq__(self, value):
        if type(value) != MeshTopo:
            return False
        return self.ndim == value.ndim

    def get_num_nodes(self):
        return self.radix ** self.ndim
    
    def get_topo_name(self):
        return "3D-mesh"


@dataclass
class TorusTopo:
    radix: int
    ndim: int

    def __eq__(self, value):
        if type(value) != TorusTopo:
            return False
        return self.ndim == value.ndim

    def get_num_nodes(self):
        return self.radix ** self.ndim
    
    def get_topo_name(self):
        return "3D-torus"


class SimID:
    @staticmethod
    def _parse_topo_name(name: str):
        name_splited = name.split("_")
        match name_splited[0]:
            case "torus":
                return TorusTopo(int(name_splited[1][1:]),
                                 int(name_splited[2][1:]))
            
            case "mesh":
                return MeshTopo(int(name_splited[1][1:]),
                                int(name_splited[2][1:]))
            
            case "circulant":
                return CirculantTopo(
                    int(name_splited[1][1:]),
                    list(map(int, name_splited[2:]))
                )
            
            case _:
                raise ValueError(f"Unknown topology {name}")

    def __init__(self, filename: str):
        parse = FILENAME_RE.search(filename)
        if parse is None:
            raise ValueError("Filename in not SimID")
        self.topo = self._parse_topo_name(parse[1])
        self.routing_func = parse[2]
        self.traffic_type = parse[3]
        self.sim_count = int(parse[4])


@dataclass
class SimRecord:
    id: SimID
    res: SimResult


def parse_results() -> list[SimRecord]:
    res = []
    for filename in tqdm(os.listdir()):
        with open(filename, "r") as file:
            try:
                rec = SimRecord(
                    id=SimID(filename),
                    res=parse_file(file),
                )
                res.append(rec)
            except SimSummaryNotFound:
                pass
            except BadSimSummary:
                print(f"Parsing error on file {filename}")
    return res


def is_route_func_ok(topo_type, func):
    if topo_type == CirculantTopo:
        return func == "min"
    else:
        return func == "dim_order"


def plot_latency(data: list[SimRecord], hops=False):
    topos = [CirculantTopo(0, [1, 4, 16]), CirculantTopo(0, [1, 4, 16, 64, 256]),
             MeshTopo(0, 3), TorusTopo(0, 3)]
    traffic = "uniform"
    fig, ax = plt.subplots()
    data.sort(key=lambda x: x.id.topo.get_num_nodes())
    for topo in topos:
        x = []
        y = []
        for d in data:
            if d.id.topo == topo and d.id.traffic_type == traffic and is_route_func_ok(type(d.id.topo), d.id.routing_func) and d.id.topo.get_num_nodes() < 1400:
                x.append(d.id.topo.get_num_nodes())
                y.append(d.res.hops_avg if hops else d.res.network_lat.avg)
        ax.plot(x, y, marker="o", label=topo.get_topo_name())
    ax.set_xlabel("Number of Nodes")
    ax.set_ylabel("Hops Average (number of hops)" if hops else "Network Latency (cycles)")
    ax.set_title("Hops" if hops else "Latency")
    ax.set_xlim(left=0, right=1400)
    ax.set_ylim(bottom=0, top=130)
    ax.grid(True)
    ax.legend()
    plt.show()


if __name__ == "__main__":
    data = parse_results()
    plot_latency(data, False)

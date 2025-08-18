import re
import io
import subprocess as sp
from model import Config, Result
from configs import (
    ISimConfig,
    CirculantConfig,
    new_mesh_config,
    new_torus_config
)


class BadSimSummary(Exception):
    pass


class SimSummaryNotFound(Exception):
    pass


class SimRunner:
    _CONFIG_CONSTRUCTORS = {
        "circulant": CirculantConfig.new_config,
        "mesh": new_mesh_config,
        "torus": new_torus_config,
    }
    _FEATURE_RE = re.compile(r"\.*= ([+-]?\d+(\.\d+(e[+-]?\d+)?)?)")

    def __init__(self, booksim_exec: str):
        self._exec = booksim_exec[2:] if booksim_exec.startswith("./") else booksim_exec
    
    def _get_float_from_line(self, line: str) -> float:
        return float(self._FEATURE_RE.search(line)[1])
    
    def _parse_simulator_output(self, stream: io.StringIO) -> Result:
        line = stream.readline()
        while line != "" and line != "====== Traffic class 0 ======\n":
            line = stream.readline()
        if line == "":
            raise SimSummaryNotFound()
        
        try:
            return Result(
                packet_latency_min=self._get_float_from_line(stream.readline()),
                packet_latency_max=self._get_float_from_line(stream.readline()),
                packet_latency_avg=self._get_float_from_line(stream.readline()),
                network_latency_min=self._get_float_from_line(stream.readline()),
                network_latency_max=self._get_float_from_line(stream.readline()),
                network_latency_avg=self._get_float_from_line(stream.readline()),
                flit_latency_min=self._get_float_from_line(stream.readline()),
                flit_latency_max=self._get_float_from_line(stream.readline()),
                flit_latency_avg=self._get_float_from_line(stream.readline()),
                fragmentation_min=self._get_float_from_line(stream.readline()),
                fragmentation_max=self._get_float_from_line(stream.readline()),
                fragmentation_avg=self._get_float_from_line(stream.readline()),
                injected_packet_rate_min=self._get_float_from_line(stream.readline()),
                injected_packet_rate_max=self._get_float_from_line(stream.readline()),
                injected_packet_rate_avg=self._get_float_from_line(stream.readline()),
                accepted_packet_rate_min=self._get_float_from_line(stream.readline()),
                accepted_packet_rate_max=self._get_float_from_line(stream.readline()),
                accepted_packet_rate_avg=self._get_float_from_line(stream.readline()),
                injected_flit_rate_min=self._get_float_from_line(stream.readline()),
                injected_flit_rate_max=self._get_float_from_line(stream.readline()),
                injected_flit_rate_avg=self._get_float_from_line(stream.readline()),
                accepted_flit_rate_min=self._get_float_from_line(stream.readline()),
                accepted_flit_rate_max=self._get_float_from_line(stream.readline()),
                accepted_flit_rate_avg=self._get_float_from_line(stream.readline()),
                injected_packet_size_avg=self._get_float_from_line(stream.readline()),
                accepted_packet_size_avg=self._get_float_from_line(stream.readline()),
                hops_avg=self._get_float_from_line(stream.readline()),
            )
        except ValueError:
            raise BadSimSummary()

    def _get_simulator_config(self, config: Config) -> ISimConfig:
        return self._CONFIG_CONSTRUCTORS[config.topo.name](
            config.topo.num_nodes,
            config.topo.links,
            config.routing_function,
            config.traffic_type,
            config.sim_count,
        )

    def sim(self, config: Config) -> Result:
        sim_config = self._get_simulator_config(config)
        sim_output = sp.run(
            f"./{self._exec} {sim_config.create_config()} 2>&1",
            shell=True,
            capture_output=True,
        )
        res = self._parse_simulator_output(
            io.StringIO(sim_output.stdout.decode()))
        res.config = config
        return res

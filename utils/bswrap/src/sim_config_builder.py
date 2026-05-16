from configs import CirculantConfig, ISimConfig, new_mesh_config, new_torus_config
from model import Config


class SimConfigBuilder:
    _CONFIG_CONSTRUCTORS = {
        "circulant": CirculantConfig.new_config,
        "mesh": new_mesh_config,
        "torus": new_torus_config,
    }

    @classmethod
    def get_simulator_config(cls, config: Config) -> ISimConfig:
        if config.topo is None:
            raise ValueError("Topology must be specified in config.")

        return cls._CONFIG_CONSTRUCTORS[config.topo.name](
            config.topo.num_nodes,
            config.topo.args,
            config.routing_function,
            config.traffic_type,
            config.sim_count,
        )

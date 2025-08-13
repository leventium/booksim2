from sqlmodel import SQLModel, Field, Relationship


class Topology(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    num_nodes: int
    links: str

    configs: list["Config"] = Relationship(back_populates="topo",
                                           cascade_delete=True)


class Config(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    topo_id: int | None = Field(default=None,
                                foreign_key="topology.id",
                                ondelete="CASCADE")
    routing_function: str
    traffic_type: str
    sim_count: int

    topo: Topology = Relationship(back_populates="configs")
    result: "Result" = Relationship(
        sa_relationship_kwargs={"uselist": False},
        back_populates="config",
        cascade_delete=True,
    )


class Result(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    config_id: int | None = Field(default=None,
                                  foreign_key="config.id",
                                  unique=True,
                                  ondelete="CASCADE")

    packet_latency_min: float
    packet_latency_max: float
    packet_latency_avg: float
    network_latency_min: float
    network_latency_max: float
    network_latency_avg: float
    flit_latency_min: float
    flit_latency_max: float
    flit_latency_avg: float
    fragmentation_min: float
    fragmentation_max: float
    fragmentation_avg: float
    injected_packet_rate_min: float
    injected_packet_rate_max: float
    injected_packet_rate_avg: float
    accepted_packet_rate_min: float
    accepted_packet_rate_max: float
    accepted_packet_rate_avg: float
    injected_flit_rate_min: float
    injected_flit_rate_max: float
    injected_flit_rate_avg: float
    accepted_flit_rate_min: float
    accepted_flit_rate_max: float
    accepted_flit_rate_avg: float
    injected_packet_size_avg: float
    accepted_packet_size_avg: float
    hops_avg: float

    config: Config = Relationship(back_populates="result")

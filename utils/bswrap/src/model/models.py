from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint


class Topology(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    num_nodes: int
    links: str

    results: list["Result"] = Relationship(back_populates="topo")


class Parameters(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    routing_function: str
    traffic_type: str
    sim_count: int

    results: list["Result"] = Relationship(back_populates="sim_params")


class Result(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("topo_id", "sim_params", name="topology and params unique"),
    )
    id: int | None = Field(default=None, primary_key=True)
    topo_id: int | None = Field(default=None, foreign_key="topology.id")
    sim_params_id: int | None = Field(default=None, foreign_key="parameters.id")
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

    topo: Topology = Relationship(back_populates="results", cascade_delete=True)
    sim_params: Parameters = Relationship(back_populates="results", cascade_delete=True)

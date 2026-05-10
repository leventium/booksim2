# bswrap

## Description
It is a wrapper for the BookSim2 network-on-chip simulatior, that increases its functionality by allowing simulating simultaneously on multiple CPUs and aggregating the results of simulations in CSV file.

### How does it work?
A: Quite simple, it takes description of the simulations targets from `user_config`, gets cartesian product of given parameters, runs multiple instanses of BookSim2 as tasks in thread pool. Finnaly it parses the output of simulator runs and writes them into CSV file.

### How do I use it?
Let's look step by step.

1. Create a python virtual invironment and install dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requirements.txt
```

2. Write the simulation configuration (details in `User Config` secrion)

3. Run it
```bash
python src/main.py -e <path_to_booksim_exec> -j <number_of_cpus>
```

### User Config

Wrapper expects `TASK_CONFIG` to be defined in `user_config.py`. `TASK_CONFIG` is a constant of type `list[SimulationTask]`.

`SimulationTask` have the folowing definition:
```python
@dataclass
class SimulationTask:
    topo_names: list[str]
    num_nodes: list[int]
    links: list[int]

    routing_funcs: list[str]
    traffic_types: list[str]
    sim_counts: list[int]
```

Meaning of the fields in this structure:
- `topo_names` - Topologies to be simulated
- `num_nodes` - Number of nodes to be simulated
- `links` - Explaindex lower
- `routing_funcs` - Routing functions to be simulated
- `traffic_types` - Traffic types to be simulated
- `sim_counts` - Number of simulations for each combination

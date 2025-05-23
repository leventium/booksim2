#!/usr/bin/env python3
import argparse


class CirculantNode:
    def __init__(self, id: int):
        self.id = id
        self.links = []

    def get_links_ids(self) -> list[int]:
        res = []
        for link in self.links:
            res.append(link.id)
        return res


class Circulant:
    @staticmethod
    def _build_circulant(num_nodes: int, links: list[int]) -> list[CirculantNode]:
        res: list[CirculantNode] = []
        for i in range(num_nodes):
            res.append(CirculantNode(i))
        for i in range(num_nodes):
            for link in links:
                link_idx = (i + link) % num_nodes
                res[i].links.append(res[link_idx])
                res[link_idx].links.append(res[i])
        return res

    def __init__(self, num_nodes: int, links: list[int]):
        if num_nodes < 3:
            raise ValueError(
                f"Error in N: N cannot be less than 3, actual {num_nodes}")
        max_link_index = (num_nodes // 2) - (1 - num_nodes % 2)
        for i, link in enumerate(links):
            if not (1 <= link <= max_link_index):
                raise ValueError(
                    f"Error in link[{i}]: link out of range, must be "
                    f"1 <= link <= {max_link_index}, actual {link}"
                )

        self._nodes: list[CirculantNode] = self._build_circulant(
            num_nodes, sorted(list(set(links))))

    def serialize_booksim(self) -> str:
        res = ""
        for node in self._nodes:
            res += f"router {node.id} node {node.id}"
            for link_id in node.get_links_ids():
                res += f" router {link_id}"
            res += "\n"
        return res
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Circulant Builder",
        description="Build description of specified circulant "
        "topology in the booksim2 anynet format",
    )
    parser.add_argument("-n", "--num-nodes", type=int)
    parser.add_argument("-l", "--links", type=str)
    args = parser.parse_args()

    topology = Circulant(
        args.num_nodes,
        list(map(int, args.links.split(","))),
    )
    print(topology.serialize_booksim())

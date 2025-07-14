import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import *


class TestingClass(unittest.TestCase):
    @parameterized.expand(gen_tcs_randomly(1000))
    def test35(self, graph: list, src: int, dst: int, method: str): # Fixed
        """Metamorphic Relation 35: Given the same graph, the same source and destination vertices,
        but with the addition of a new edge with weight 0 between any two vertices, the result should remain unchanged."""
        # Get source output
        source_out = shortest_path(graph, method=method)

        # Add a new edge with weight 0 between any two vertices
        follow_graph = graph.copy()
        follow_graph[src][dst] = 0

        # Get follow-up output
        follow_out = shortest_path(follow_graph, method=method)

        # Verification
        self.assertTrue(np.array_equal(source_out, follow_out))


if __name__ == "__main__":
    unittest.main()

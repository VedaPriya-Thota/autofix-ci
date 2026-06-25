import networkx as nx


class DependencyGraphBuilder:

    def build(self, repo_context):

        G = nx.DiGraph()

        files = repo_context.keys()

        for file in files:
            G.add_node(file)

        # simple heuristic edges
        if "requirements.txt" in files:
            G.add_edge("requirements.txt", "runtime")

        if "Dockerfile" in files:
            G.add_edge("Dockerfile", "build")

        if ".github/workflows/main.yml" in files:
            G.add_edge("workflow", "build")

        return {
            "nodes": list(G.nodes),
            "edges": list(G.edges)
        }
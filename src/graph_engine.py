import networkx as nx

def build_dependency_graph(entities_df, dependencies_df):
    graph = nx.DiGraph()

    for _, row in entities_df.iterrows():
        graph.add_node(
            row["id"],
            name=row["name"],
            type=row["type"],
            criticality=int(row["criticality"]),
            owner_team=row["owner_team"],
        )

    for _, row in dependencies_df.iterrows():
        graph.add_edge(
            row["source"],
            row["target"],
            relationship=row["relationship"],
        )

    return graph

def get_impacted_nodes(graph, target_node, max_depth=3):
    if target_node not in graph:
        return []

    impacted = []
    visited = set([target_node])
    queue = [(target_node, 0, "SELF")]

    while queue:
        current, depth, relationship = queue.pop(0)

        if depth > 0:
            impacted.append({
                "node_id": current,
                "depth": depth,
                "relationship_path": relationship,
                "name": graph.nodes[current].get("name"),
                "type": graph.nodes[current].get("type"),
                "criticality": graph.nodes[current].get("criticality"),
                "owner_team": graph.nodes[current].get("owner_team"),
            })

        if depth < max_depth:
            # Downstream dependencies
            for neighbor in graph.successors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    edge_rel = graph.edges[current, neighbor].get("relationship", "DEPENDS")
                    queue.append((neighbor, depth + 1, edge_rel))

            # Reverse impact: consumers/users of the changed component
            for predecessor in graph.predecessors(current):
                if predecessor not in visited:
                    visited.add(predecessor)
                    edge_rel = graph.edges[predecessor, current].get("relationship", "USES")
                    queue.append((predecessor, depth + 1, f"REVERSE_{edge_rel}"))

    return impacted
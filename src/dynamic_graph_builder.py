import networkx as nx


def build_dynamic_graph(entities_df, dependencies_df):
    graph = nx.DiGraph()

    if entities_df.empty:
        return graph

    for _, row in entities_df.iterrows():
        graph.add_node(
            row["id"],
            name=row["name"],
            type=row["type"],
            criticality=int(row["criticality"]),
            owner_team=row["owner_team"],
        )

    if not dependencies_df.empty:
        for _, row in dependencies_df.iterrows():
            graph.add_edge(
                row["source"],
                row["target"],
                relationship=row["relationship"],
            )

    return graph
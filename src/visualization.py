from pyvis.network import Network
import tempfile

TYPE_COLOR = {
    "Application": "#4C78A8",
    "Service": "#F58518",
    "API": "#54A24B",
    "Database": "#B279A2",
    "Pipeline": "#E45756",
    "Business Capability": "#72B7B2",
}

def create_pyvis_graph(graph, impacted_nodes=None, target_node=None):
    impacted_nodes = set(impacted_nodes or [])
    net = Network(height="650px", width="100%", directed=True, bgcolor="#ffffff", font_color="#222222")

    for node, attrs in graph.nodes(data=True):
        is_target = node == target_node
        is_impacted = node in impacted_nodes

        label = attrs.get("name", node)
        title = f"Type: {attrs.get('type')}<br>Owner: {attrs.get('owner_team')}<br>Criticality: {attrs.get('criticality')}"
        color = "#D62728" if is_target else ("#FFBF00" if is_impacted else TYPE_COLOR.get(attrs.get("type"), "#999999"))
        size = 32 if is_target else (24 if is_impacted else 16)

        net.add_node(node, label=label, title=title, color=color, size=size)

    for source, target, attrs in graph.edges(data=True):
        net.add_edge(source, target, title=attrs.get("relationship"), label=attrs.get("relationship"))

    net.repulsion(node_distance=220, spring_length=180)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    net.save_graph(temp_file.name)
    return temp_file.name
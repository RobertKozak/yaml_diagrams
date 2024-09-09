import yaml
import os
from typing import Dict, Any, Union, List
from diagrams import Diagram, Cluster, Edge
from diagrams.aws import compute, network, security, storage
from diagrams.azure import compute as azure_compute, network as azure_network
from diagrams.gcp import compute as gcp_compute, network as gcp_network
from diagrams.k8s import compute as k8s_compute, network as k8s_network
from diagrams.onprem import compute as onprem_compute, network as onprem_network
from diagrams.generic import compute as generic_compute, network as generic_network

class YamlToDiagramsConverter:
    def __init__(self, yaml_content: str):
        self.yaml_data = yaml.safe_load(yaml_content)
        self.node_definitions: Dict[str, Any] = {}
        self.connections: List[Dict[str, Any]] = []
        self.node_types = self._get_node_types()
        self.diagram = None

    def _get_node_types(self) -> Dict[str, Any]:
        node_types = {}
        for provider in [compute, network, security, storage, azure_compute, azure_network, 
                         gcp_compute, gcp_network, k8s_compute, k8s_network, 
                         onprem_compute, onprem_network, generic_compute, generic_network]:
            provider_name = provider.__name__.split('.')[-1]
            for attr_name in dir(provider):
                attr = getattr(provider, attr_name)
                if isinstance(attr, type) and attr.__module__ == provider.__name__:
                    node_types[f"{provider_name}.{attr_name}"] = attr
        return node_types

    def _find_closest_match(self, node_type: str) -> str:
        parts = node_type.split('.')
        if len(parts) == 2:
            provider, node = parts
            for key in self.node_types.keys():
                if key.lower() == node_type.lower():
                    return key
            for key in self.node_types.keys():
                if key.lower().endswith(node.lower()):
                    return key
        return node_type

    def process_node(self, node: Dict[str, Any], parent: Union[Diagram, Cluster] = None) -> Any:
        node_type = self._find_closest_match(node['type'])
        node_class = self.node_types.get(node_type)
        if not node_class:
            available_types = ", ".join(sorted(self.node_types.keys()))
            raise ValueError(f"Unknown node type: {node_type}. Available types: {available_types}")
        
        node_name = node['name']
        node_count = node.get('count', 1)
        node_args = node.get('args', {})
        
        if node_count > 1:
            nodes = [node_class(f"{node_name} {i+1}", **node_args) for i in range(node_count)]
            self.node_definitions[node_name] = nodes
            return nodes
        else:
            node_instance = node_class(node_name, **node_args)
            self.node_definitions[node_name] = node_instance
            return node_instance

    def process_cluster(self, cluster: Dict[str, Any], parent: Union[Diagram, Cluster] = None) -> Cluster:
        with Cluster(cluster['name']) as c:
            for node in cluster.get('nodes', []):
                self.process_node(node, c)
            
            for sub_cluster in cluster.get('clusters', []):
                self.process_cluster(sub_cluster, c)
            
            return c

    def process_connections(self):
        print("Processing connections...")
        for connection in self.yaml_data.get('connections', []):
            print(f"Connection: {connection}")
            from_key = connection['from']
            to_key = connection['to']
            
            def get_nodes(key):
                if isinstance(key, list):
                    nodes = []
                    for k in key:
                        n = self.node_definitions.get(k)
                        if n is not None:
                            if isinstance(n, list):
                                nodes.extend(n)
                            else:
                                nodes.append(n)
                    return nodes
                else:
                    return self.node_definitions.get(key)
            
            from_nodes = get_nodes(from_key)
            to_nodes = get_nodes(to_key)
            
            print(f"From nodes: {from_nodes}")
            print(f"To nodes: {to_nodes}")
            
            if from_nodes is None:
                print(f"Warning: Node '{from_key}' not found in node_definitions")
                continue
            if to_nodes is None:
                print(f"Warning: Node '{to_key}' not found in node_definitions")
                continue
            
            edge_args = connection.get('edge', {})
            
            if not isinstance(from_nodes, list):
                from_nodes = [from_nodes]
            if not isinstance(to_nodes, list):
                to_nodes = [to_nodes]
            
            for from_node in from_nodes:
                for to_node in to_nodes:
                    from_node >> Edge(**edge_args) >> to_node


    def process_outputs(self):
        print("Processing outputs...")
        for output in self.yaml_data.get('outputs', []):
            print(f"Output: {output}")
            from_key = output['from']
            
            if isinstance(from_key, list):
                from_nodes = []
                for key in from_key:
                    nodes = self.node_definitions.get(key)
                    if nodes is not None:
                        if isinstance(nodes, list):
                            from_nodes.extend(nodes)
                        else:
                            from_nodes.append(nodes)
            else:
                from_nodes = self.node_definitions.get(from_key)
            
            print(f"From nodes: {from_nodes}")
            
            if from_nodes is None:
                print(f"Warning: Node '{from_key}' not found in node_definitions")
                continue
            
            if not isinstance(from_nodes, list):
                from_nodes = [from_nodes]
            for node in from_nodes:
                node << Edge(label=output['name'])

    def generate_diagram(self):
        diagram_config = self.yaml_data['diagram']
        output_file = self.yaml_data.get('output_file', 'diagram')
        
        # Remove file extension if present
        output_file = os.path.splitext(output_file)[0]

        with Diagram(diagram_config['name'], filename=output_file, 
                     direction=diagram_config.get('direction', 'TB'), show=False) as d:
            print("Processing clusters and nodes...")
            for cluster in self.yaml_data.get('clusters', []):
                self.process_cluster(cluster, d)
            
            for node in self.yaml_data.get('nodes', []):
                self.process_node(node, d)
            
            print("Node definitions:", self.node_definitions)
            
            self.process_connections()
            self.process_outputs()

def convert_yaml_to_diagrams(yaml_content: str):
    converter = YamlToDiagramsConverter(yaml_content)
    converter.generate_diagram()
    print(f"Diagram generated and saved")

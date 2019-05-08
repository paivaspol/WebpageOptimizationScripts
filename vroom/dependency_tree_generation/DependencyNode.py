class DependencyNode:

    def __init__(self):
        self.documentURL = ''
        self.parent = ''
        self.url = ''
        self.priority = ''
        self.found_index = -1
        self.request_id = ''
        self.type = ''
        self.children = []
        self.is_root = False
        self.is_leaf = False
    
    def populate_node(self, node_dict):
        self.documentURL = node_dict['documentURL']
        self.parent = node_dict['parent']
        self.url = node_dict['url']
        self.priority = node_dict['priority']
        self.found_index = node_dict['found_index']
        self.request_id = node_dict['request_id']
        self.type = node_dict['type']
        self.children = node_dict['children']
        self.is_root = node_dict['isRoot']
        self.is_leaf = node_dict['isLeaf']

        if self.parent is not None and self.parent.endswith('/'):
            self.parent = self.parent[:len(self.parent) - 1]

    def __str__(self):
        return '[Node] ' + self.url

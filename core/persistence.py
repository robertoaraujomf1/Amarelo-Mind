import json

class PersistenceManager:
    @staticmethod
    def save_to_file(file_path, scene):
        from items.shapes import MindMapNode
        data = {"objects": []}
        for item in scene.items():
            if isinstance(item, MindMapNode):
                obj_data = {
                    "pos": [item.pos().x(), item.pos().y()],
                    "size": [item.rect().width(), item.rect().height()],
                    "colors": item.current_colors
                }
                data["objects"].append(obj_data)
        
        with open(file_path, 'w') as f:
            json.dump(data, f)

    @staticmethod
    def load_from_file(file_path, scene):
        from items.shapes import MindMapNode
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        scene.clear()
        for obj in data["objects"]:
            node = MindMapNode(obj["pos"][0], obj["pos"][1])
            node.setRect(0, 0, obj["size"][0], obj["size"][1])
            scene.addItem(node)
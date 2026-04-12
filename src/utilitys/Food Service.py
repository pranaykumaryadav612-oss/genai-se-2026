class FoodService:
    def __init__(self):
        self.menu = self.load_menu()
    
    def load_menu(self):
        import json
        with open('menu.json', 'r') as f:
            return json.load(f)
    
    def add_to_menu(self, item):
        self.menu.append(item)
        self.save_menu()
    
    def save_menu(self):
        import json
        with open('menu.json', 'w') as f:
            json.dump(self.menu, f)
    
    def order_food(self, item_name):
        for item in self.menu:
            if item['name'] == item_name:
                return f"Ordering {item_name}"
        return "Item not found in menu"


filename: order_system.py
code:
from src.utilitys.FoodService import FoodService

class OrderSystem:
    def __init__(self):
        self.food_service = FoodService()
    
    def place_order(self, item_name):
        return self.food_service.order_food(item_name)


filename: menu.json
code:
[
    {"name": "Pizza", "price": 10.99},
    {"name": "Burger", "price": 9.99},
    {"name": "Biryani", "price": 12.99}
]
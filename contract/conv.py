class Product:
    def __init__(self, label, price):
        self.label = label
        self.price = price


product = Product("Apple", 1.2)

# Normally:
product.label = "Banana"
product.price = 0.8

# With setattr:
setattr(product, "label", "Banana")
setattr(product, "price", 0.8)

print(product.label)  # Banana
print(product.price)  # 0.8

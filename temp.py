from wake_abc.scraper import get_inventory, get_product

PRODUCT_NAME = "Malört"

print(f"Searching for {PRODUCT_NAME}...")
inventory = get_inventory(PRODUCT_NAME)
product = get_product(PRODUCT_NAME)

print(f"\nSearch complete for {PRODUCT_NAME}:")
print(f"* Product details for {product}")
print("* Found locations:")
print(*inventory, sep="\n")

# TODO Sort by closest to given address?
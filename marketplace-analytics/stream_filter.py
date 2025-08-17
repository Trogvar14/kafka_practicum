import faust, os

BROKER = os.getenv("KAFKA_BROKER", "kafka://localhost:19092")

app = faust.App("product_filter", broker=BROKER)

class Product(faust.Record, serializer='json', isodates=True, validate=False):
    product_id: str
    name: str
    description: str = None
    price: dict = None
    category: str = None
    brand: str = None
    stock: dict = None
    sku: str = None
    tags: list = None
    images: list = None
    specifications: dict = None
    created_at: str = None
    updated_at: str = None
    index: str = None
    store_id: str = None

products_topic = app.topic("products", value_type=Product)
filtered_topic = app.topic("products_filtered", value_type=Product)

BANNED = set(x.strip() for x in open("banned_list.txt", "r", encoding="utf-8") if x.strip())

@app.agent(products_topic)
async def filter_products(stream):
    async for product in stream:
        if product.name in BANNED:
            print(f"[STREAM] Товар ЗАПРЕЩЁН и отфильтрован: {product.name}")
        else:
            await filtered_topic.send(value=product)
            print(f"[STREAM] Пропущен: {product.name}")

if __name__ == "__main__":
    app.main()

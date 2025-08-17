import json, click
from confluent_kafka import Producer
P = Producer({"bootstrap.servers":"localhost:19092","security.protocol":"ssl","ssl.ca.location":"certs/ca.crt"})
@click.command()
@click.argument("product_id")
@click.option("--unban", is_flag=True, help="снять запрет")
def main(product_id, unban):
    evt = {"product_id":product_id, "action":"unban" if unban else "ban"}
    P.produce("shop.banned", key=product_id.encode(), value=json.dumps(evt).encode()); P.flush()
    click.echo("ok")
if __name__=="__main__": main()

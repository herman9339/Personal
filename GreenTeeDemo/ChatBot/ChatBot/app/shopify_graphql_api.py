import requests
from utils import SHOP_URL, SHOP_TOKEN

GRAPHQL_URL = f"https://{SHOP_URL}/admin/api/2023-04/graphql.json"
HEADERS = {
    "X-Shopify-Access-Token": SHOP_TOKEN,
    "Content-Type": "application/json",
}
def fetch_and_print_order_by_name(order_name):
    """
    Fetches order details by order name and pretty-prints them.
    """
    import requests
    from utils import SHOP_URL, SHOP_TOKEN

    GRAPHQL_URL = f"https://{SHOP_URL}/admin/api/2023-04/graphql.json"
    HEADERS = {
        "X-Shopify-Access-Token": SHOP_TOKEN,
        "Content-Type": "application/json",
    }

    # Remove # if present for the search
    search_name = order_name.lstrip("#")
    query = """
    query ($name: String!) {
      orders(first: 1, query: $name) {
        edges {
          node {
            id
            name
            email
            createdAt
            note
            shippingAddress {
              address1
              address2
              city
              province
              zip
              country
            }
            totalPriceSet { shopMoney { amount currencyCode } }
            customer { firstName lastName email }
            lineItems(first: 50) {
              edges {
                node {
                  name
                  quantity
                  sku
                  originalUnitPriceSet { shopMoney { amount currencyCode } }
                  product {
                    handle
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    variables = {
        "name": f"name:{search_name}"
    }
    response = requests.post(
        GRAPHQL_URL,
        headers=HEADERS,
        json={"query": query, "variables": variables}
    )
    data = response.json()
    if "errors" in data:
        print(f"GraphQL errors: {data['errors']}")
        return None
    orders = data.get("data", {}).get("orders", {}).get("edges", [])
    if not orders:
        print("No order found with that name.")
        return None
    order = orders[0]["node"]

    # Pretty print
    print("\nOrder Details:")
    print(f"  Name: {order.get('name')}")
    print(f"  Email: {order.get('email')}")
    print(f"  Created At: {order.get('createdAt')}")
    print(f"  Customer: {order.get('customer', {}).get('firstName', '')} {order.get('customer', {}).get('lastName', '')}")
    print(f"  Total: {order.get('totalPriceSet', {}).get('shopMoney', {}).get('amount', '')} {order.get('totalPriceSet', {}).get('shopMoney', {}).get('currencyCode', '')}")
    print(f"  Notes: {order.get('note', '')}")
    # Shipping Address
    addr = order.get('shippingAddress', {})
    if addr:
        print("  Shipping Address:")
        print(f"    {addr.get('address1', '')}")
        if addr.get('address2'):
            print(f"    {addr.get('address2')}")
        print(f"    {addr.get('city', '')}, {addr.get('province', '')} {addr.get('zip', '')}")
        print(f"    {addr.get('country', '')}")
    print(f"  Line Items:")
    for edge in order.get('lineItems', {}).get('edges', []):
        item = edge['node']
        handle = item.get('product', {}).get('handle', 'N/A') if item.get('product') else 'N/A'
        print(f"    - Name: {item['name']}")
        print(f"      SKU: {item['sku']}")
        print(f"      Product Handle: {handle}")
        print(f"      Quantity: {item['quantity']}")
        print(f"      Price: {item['originalUnitPriceSet']['shopMoney']['amount']} {item['originalUnitPriceSet']['shopMoney']['currencyCode']}")
        print()


def get_product_by_handle(handle):
    """
    Fetch product info by handle using Shopify GraphQL Admin API.
    Returns product description, all variants (name, sku, inventory), and product link.
    """
    query = """
    query ($handle: String!) {
      productByHandle(handle: $handle) {
        id
        title
        descriptionHtml
        handle
        onlineStoreUrl
        variants(first: 50) {
          edges {
            node {
              id
              title
              sku
              inventoryQuantity
            }
          }
        }
      }
    }
    """
    variables = {"handle": handle}
    response = requests.post(
        GRAPHQL_URL,
        headers=HEADERS,
        json={"query": query, "variables": variables}
    )
    data = response.json()
    if "errors" in data:
        print(f"GraphQL errors: {data['errors']}")
        return None
    product = data.get("data", {}).get("productByHandle")
    if not product:
        print("No product found with that handle.")
        return None
    return product



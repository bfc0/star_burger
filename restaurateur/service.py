
def get_restaraunts_can_handle_order(availability, products_required, coordservice, order):
    restaurants_can_handle = []
    for restaurant, r_products in availability.items():
        if products_required - r_products:
            continue
        distance = coordservice.get_distance(restaurant.address, order.address)
        restaurants_can_handle.append(
            (restaurant.id, str(restaurant), distance))

    restaurants_can_handle.sort(
        key=lambda x: x[1] if x[1] is not None else float("inf"))

    return restaurants_can_handle

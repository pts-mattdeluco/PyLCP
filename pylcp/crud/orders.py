from pylcp.crud import base as crud


class Order(crud.LCPCrud):

    def create(self, order_type, data, **kwargs):
        """ Create an order. Any kwargs will be added as top-level parameters in the request payload.
        """
        payload = self._create_payload(order_type, data, **kwargs)

        return super(Order, self).create('/orders/', payload)

    def _create_payload(self, order_type, data, **kwargs):
        payload = {"orderType": order_type,
                   "data": data}

        payload.update(kwargs)

        return payload

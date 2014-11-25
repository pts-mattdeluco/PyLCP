import crud


class Order(crud.LCP):

    def create(self, url, order_type, data, **kwargs):
        """ Create an offerset. Any kwargs will be added as top-level parameters in the request payload.
        """
        payload = self._create_payload(order_type, data)

        return super(Order, self).create(url, payload)

    def _create_payload(self, order_type, data, **kwargs):
        payload = {"orderType": order_type,
                   "data": data}

        payload.update(kwargs)

        return payload

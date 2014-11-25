import crud


class Credit(crud.LCP):

    def create(self, url, amount, member_validation, pic=None, **kwargs):
        """ Create a credit. Any kwargs will be added as top-level parameters in the request payload.
        """
        payload = self._create_payload(amount, member_validation, pic=None, **kwargs)

        return super(Credit, self).create(url, payload)

    def _create_payload(self, amount, member_validation, pic=None, **kwargs):
        payload = {"amount": amount,
                   "memberValidation": member_validation}

        if pic is not None:
            payload['pic'] = pic

        payload.update(kwargs)

        return payload

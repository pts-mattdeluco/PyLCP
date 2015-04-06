from pylcp.crud import base as crud


class Credit(crud.LCPCrud):
    def create(self, path, amount, member_validation, pic=None, credit_type=None, **kwargs):
        """ Create a credit. Any kwargs will be added as top-level parameters in the request payload.
        """
        payload = _create_payload(amount, member_validation, pic, credit_type, **kwargs)

        return super(Credit, self).create(path, payload)


class Debit(crud.LCPCrud):
    def create(self, path, amount, member_validation, pic=None, **kwargs):
        """ Create a debit. Any kwargs will be added as top-level parameters in the request payload.
        """
        payload = _create_payload(amount, member_validation, pic, **kwargs)

        return super(Debit, self).create(path, payload)


def _create_payload(amount, member_validation, pic=None, credit_type=None, **kwargs):
        payload = {"amount": amount,
                   "memberValidation": member_validation}

        if pic is not None:
            payload['pic'] = pic

        if credit_type:
            payload['creditType'] = credit_type

        payload.update(kwargs)

        return payload

from pylcp.crud import base as crud


class LoyaltyProgram(crud.LCPCrud):
    def read(self, loyalty_program_id):
        path = '/lps/{}'.format(loyalty_program_id)
        return super(LoyaltyProgram, self).read(path)

﻿# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __openerp__.py
#
##############################################################################

from openerp import api, models
from openerp.tools import mod10r
from openerp.addons.sponsorship_compassion.models.product import GIFT_NAMES

import logging

logger = logging.getLogger(__name__)


class GenerateGiftWizard(models.TransientModel):
    """ This wizard generates a Gift Invoice for a given contract. """
    _inherit = 'generate.gift.wizard'

    @api.multi
    def _setup_invoice(self, contract, invoice_date):
        res = super(GenerateGiftWizard, self)._setup_invoice(contract,
                                                             invoice_date)
        res['bvr_reference'] = self.generate_bvr_reference(
            contract, self.product_id)
        return res

    @api.model
    def generate_bvr_reference(self, contract, product):
        product = product.with_context(lang='en_US')
        ref = contract.partner_id.ref
        bvr_reference = '0' * (9 + (7 - len(ref))) + ref
        commitment_number = str(contract.commitment_number)
        bvr_reference += '0' * (5 - len(commitment_number)) + commitment_number
        # Type of gift
        bvr_reference += str(GIFT_NAMES.index(product.name) + 1)
        bvr_reference += '0' * 4

        if contract.group_id.payment_term_id and \
                'LSV' in contract.group_id.payment_term_id.name:
            # Get company BVR adherent number
            user = self.env.user
            bank_obj = self.env['res.partner.bank']
            company_bank = bank_obj.search([
                ('partner_id', '=', user.company_id.partner_id.id),
                ('bvr_adherent_num', '!=', False)])
            if company_bank:
                bvr_reference = company_bank.bvr_adherent_num +\
                    bvr_reference[9:]
        if len(bvr_reference) == 26:
            return mod10r(bvr_reference)

        return False

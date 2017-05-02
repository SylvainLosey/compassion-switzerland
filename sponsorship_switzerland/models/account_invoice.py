# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __openerp__.py
#
##############################################################################

from openerp import api, models, fields, _
from openerp.exceptions import UserError
from openerp.tools import mod10r
from openerp.addons.sponsorship_compassion.models.product import \
    GIFT_CATEGORY, SPONSORSHIP_CATEGORY, FUND_CATEGORY


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    invoice_type = fields.Selection([
        ('sponsorship', 'Sponsorship'),
        ('gift', 'Gift'),
        ('fund', 'Fund donation'),
        ('other', 'Other'),
    ], compute='compute_invoice_type', store=True)

    @api.depends('invoice_line_ids', 'state')
    @api.multi
    def compute_invoice_type(self):
        for invoice in self.filtered(lambda i: i.state in ('open', 'paid')):
            categories = invoice.with_context(lang='en_US').mapped(
                'invoice_line_ids.product_id.categ_name')
            if SPONSORSHIP_CATEGORY in categories:
                invoice.invoice_type = 'sponsorship'
            elif GIFT_CATEGORY in categories:
                invoice.invoice_type = 'gift'
            elif FUND_CATEGORY in categories:
                invoice.invoice_type = 'fund'
            else:
                invoice.invoice_type = 'other'

    @api.multi
    def action_date_assign(self):
        """Method called when invoice is validated.
            - Add BVR Reference if payment term is LSV and no reference is
              set.
            - Prevent validating invoices missing related contract.
        """
        for invoice in self.filtered('payment_term_id'):
            if 'LSV' in invoice.payment_term_id.name \
                    and not invoice.bvr_reference:
                seq = self.env['ir.sequence']
                ref = mod10r(seq.next_by_code('contract.bvr.ref'))
                invoice.write({'bvr_reference': ref})
            for invl in invoice.invoice_line_ids:
                if not invl.contract_id and invl.product_id.categ_name in (
                        SPONSORSHIP_CATEGORY, GIFT_CATEGORY):
                    raise UserError(
                        _("Invoice %s for '%s' is missing a sponsorship.") %
                        (str(invoice.id), invoice.partner_id.name))

        return super(AccountInvoice, self).action_date_assign()

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_over_credit_limit = fields.Boolean(string='Over Credit Limit', default=False)

    @api.model
    def create(self, vals):
        if 'partner_id' in vals:
            partner = self.env['res.partner'].browse(vals['partner_id'])
            if 'amount_total' not in vals:
                    order = self.env['sale.order'].new(vals)
                    order._amount_all()
                    vals['amount_total'] = order.amount_total

            if partner.credit + vals['amount_total'] > partner.credit_limit_compute:
                vals['is_over_credit_limit'] = True
        return super(SaleOrder, self).create(vals)
    
    def action_confirm(self):
        if not self.is_over_credit_limit:
            super(SaleOrder, self).action_confirm()
        else:
            current_user = self.env.user
            group_id = self.env.ref('custom_credit_limit.group_allow_over_credit_limit').id 
            check_permission = group_id in current_user.groups_id.ids

            if not check_permission:
                raise UserError("You do not have the permission to confirm the customer over credit limited.")

            if self.state not in ['draft', 'sent']:
                raise UserError("You can only confirm in 'Draft' or 'Sent' state.")
            
            super(SaleOrder, self).action_confirm()
        return True

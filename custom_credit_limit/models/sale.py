from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_over_credit_limit = fields.Boolean(string='Over Credit Limit',compute="compute_is_check", default=False)

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
    
    def compute_is_check(self):
        for record in self:
            partner = record.partner_id
            if partner.credit + record.amount_total > partner.credit_limit_compute:
                record.is_over_credit_limit = True
            else:
                record.is_over_credit_limit = False

    @api.model
    def open_sale_order(self):
        for order in self:
            if order.is_over_credit_limit:
                order.action_post()
        return True

    @api.onchange('is_over_credit_limit')
    def _onchange_is_over_credit_limit(self):
        if self.is_over_credit_limit:
            self.action_post()
        
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

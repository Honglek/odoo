from odoo import models, fields, api

class SaleActivities(models.Model):
    _name = 'sale.activities'
    _auto = False

    
    date = fields.Datetime('Execution Date')
    user = fields.Char('User Person')
    model = fields.Char('Model Reference')
    record_name = fields.Char('Reference')
    province_name = fields.Char('Province')
    district_name = fields.Char('District')
    body = fields.Char('Log note information')

    def init(self):
        # create python coce to u8pdate province name and distric name to contact table
        query = """
            UPDATE res_partner a
            SET province_name = b.name
            FROM kh_province b
            WHERE a.kh_province = b.id and coalesce(a.province_name,'') = '';

            UPDATE res_partner a
            SET district_name = b.name
            FROM kh_district b
            WHERE a.kh_district = b.id and coalesce(a.province_name,'') = '';
        """
        
        # Execute the query
        self.env.cr.execute(query)

        self._cr.execute("""
            CREATE OR REPLACE VIEW sale_activities AS (
                SELECT row_number() OVER() as id,
                    mm.date as date,
                    case 
                        when mm.model = 'sale.order' then 'Sale'
                        when mm.model = 'res.partner' then 'Contact'
                        when mm.model = 'account.move' then 'Accounting'
                        when mm.model = 'crm.lead' then 'CRM'
                        when mm.model = 'purchase.order' then 'Purchase'
                        when mm.model = 'purchase.requisition' then 'Purchase'
                        when mm.model = 'purchase.request' then 'Purchase'
                        when mm.model = 'purchase.request.line' then 'Purchase'
                        when mm.model = 'stock.picking' then 'Inventory'
                        when mm.model = 'stock.scrap' then 'Inventory'
                        when mm.model = 'stock.inventory' then 'Inventory'
                        when mm.model = 'stock.landed.cost' then 'Inventory'
                        when mm.model = 'hr.employee' then 'Employees'
                        when mm.model = 'hr.employee' then 'Employees'
                        when mm.model = 'hr.contract' then 'Employees'
                        when mm.model = 'fleet.vehicle' then 'Fleet'
                        when mm.model = 'fleet.vehicle.log.contract' then 'Fleet'
                    else
                        mm.model
                    end as model,
                    mm.record_name as record_name,
                    REGEXP_REPLACE(mm.body, '<[^>]*>', '', 'g') AS body,
                    rp.name as user,
                    p.province_name as province_name,
                    p.district_name as district_name
                FROM mail_message mm
                JOIN res_partner rp ON mm.author_id = rp.id
                left join res_partner p on p.id = mm.res_id
                WHERE mm.message_type = 'comment'
				ORDER BY mm.date DESC
            )
        """)

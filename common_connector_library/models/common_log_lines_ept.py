# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api

class CommonLogLineEpt(models.Model):
    _name = "common.log.lines.ept"
    _description = "Common log line for all connector"

    product_id = fields.Many2one('product.product', 'Product')
    order_ref = fields.Char('Order Reference')
    default_code = fields.Char('SKU')
    log_book_id = fields.Many2one('common.log.book.ept', ondelete="cascade")
    message = fields.Text()
    model_id = fields.Many2one("ir.model", string="Model")
    res_id = fields.Integer("Record ID")
    mismatch_details = fields.Boolean(string='Mismatch Detail', help="Mismatch Detail of process order")
    file_name = fields.Char(string='File Name')
    sale_order_id = fields.Many2one(comodel_name='sale.order', string='Sale Order')

    @api.model
    def get_model_id(self, model_name):
        """
        This method is used to get model id
        :param model_name: model_name
        :return: model_id
        """
        model = self.env['ir.model'].sudo().search([('model', '=', model_name)])
        if model:
            return model.id
        return False

    def create_log_lines(
            self, message, model_id, res_id, log_book_id, default_code='',order_ref='',product_id=False):
        """ Prepare vals for the log line.
            :param message: Error/log message
            :param model_id: Record of model
            :param res_id: Res Id(Here we can set process record id).
            :param log_book_id: Record of log book.
            @return: vals
        """
        vals = {'message': message,
                'model_id': model_id,
                'res_id': res_id.id if res_id else False,
                'log_book_id': log_book_id.id if log_book_id else False,
                'default_code':default_code,
                'order_ref': order_ref,
                'product_id':product_id
                }
        log_line = self.create(vals)
        return log_line

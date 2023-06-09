# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import models


class WooManualQueueProcessEpt(models.TransientModel):
    """
    Common model for handling the manual queue processes.
    """
    _name = "woo.manual.queue.process.ept"
    _description = "WooCommerce Manual Queue Process"

    def process_queue_manually(self):
        """
        It calls different methods queue type wise.
        @author: Maulik Barad on Date 08-Nov-2019.
        """
        queue_type = self._context.get("queue_type", "")
        if queue_type == "order":
            self.process_order_queue_manually()
        elif queue_type == "customer":
            self.process_customer_queue_manually()
        elif queue_type == "product":
            self.process_products_queue_manually()
        elif queue_type == 'coupon':
            self.process_coupon_queue_manually()
        elif queue_type == "export_stock":
            self.process_export_stock_queue_manually()
        return {'type': 'ir.actions.client',
                'tag': 'reload'}

    def process_export_stock_queue_manually(self):
        """
        This method used to process the export stock queue manually.
        @author: Yagnik Joshi @Emipro Technologies Pvt.Ltd on date 31-Aug-2022.
        Task Id : 201222
        """
        model = self._context.get('active_model')
        woo_export_stock_queue_line_obj = self.env["woo.export.stock.queue.line.ept"]
        export_stock_queue_ids = self._context.get('active_ids')
        if model == "woo.order.data.queue.line.ept":
            export_stock_queue_ids = woo_export_stock_queue_line_obj.search(
                [('id', 'in', export_stock_queue_ids)]).mapped(
                "woo_export_stock_queue_id").ids
        self.env.cr.execute(
            """update woo_export_stock_queue_ept set is_process_queue = False where is_process_queue = True""")
        self._cr.commit()
        for export_stock_queue_id in export_stock_queue_ids:
            export_stock_queue_line_batch = woo_export_stock_queue_line_obj.search(
                [("export_stock_queue_id", "=", export_stock_queue_id),
                 ("state", "in", ('draft', 'failed'))])
            export_stock_queue_line_batch.process_export_stock_queue_data()
        return True

    def process_order_queue_manually(self):
        """
        This method used to process the order queue manually.
        @author: Maulik Barad on Date 08-Nov-2019.
        """
        order_data_queue_obj = self.env['woo.order.data.queue.ept']
        order_queue_ids = order_data_queue_obj.browse(self._context.get('active_ids'))

        self.env.cr.execute(
            """update woo_order_data_queue_ept set is_process_queue = False where is_process_queue = True""")
        self._cr.commit()
        for order_queue_id in order_queue_ids:
            order_queue_line_batch = order_queue_id.order_data_queue_line_ids.filtered(
                lambda x: x.state in ["draft", "failed"])
            order_queue_line_batch.process_order_queue_line()

        return True

    def process_customer_queue_manually(self):
        """This method is used for import customer manually instead of cron.
            It'll fetch only those queues which is not 'completed' and
            process only those queue lines which is not 'done'.
            @param : self
            @return: True
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 31 August 2020 .
            Task_id: 165956
        """
        customer_data_queue_obj = self.env['woo.customer.data.queue.ept']
        customer_queues = customer_data_queue_obj.browse(
            self._context.get('active_ids', False)).filtered(lambda x: x.state != "done")
        for customer_queue in customer_queues:
            customer_queue_lines = customer_queue.queue_line_ids.filtered(lambda x: x.state in ['draft', 'failed'])
            if customer_queue_lines:
                customer_queue_lines.process_woo_customer_queue_lines_directly()
        return True

    def process_products_queue_manually(self):
        """
        This method used to process the products queue manually.
        @author: Dipak Gogiya
        """
        product_data_queue_obj = self.env['woo.product.data.queue.ept']
        product_queue_ids = product_data_queue_obj.browse(self._context.get('active_ids')).filtered(
            lambda x: x.state != 'done')
        self.env.cr.execute(
            """update woo_product_data_queue_ept set is_process_queue = False where is_process_queue = True""")
        self._cr.commit()
        for woo_product_queue_id in product_queue_ids:
            woo_product_queue_line_ids = woo_product_queue_id.queue_line_ids.filtered(
                lambda x: x.state in ['draft', 'failed'])
            if woo_product_queue_line_ids:
                woo_product_queue_line_ids.process_woo_product_queue_lines()
        return True

    def process_coupon_queue_manually(self):
        """
        This method used to process the coupon queue manually.
        @author: Nilesh Parmar on Date 31 Dec 2019.
        """
        coupon_data_queue_obj = self.env['woo.coupon.data.queue.ept']
        coupon_queue_ids = coupon_data_queue_obj.browse(
            self._context.get('active_ids'))

        for coupon_queue_id in coupon_queue_ids:
            coupon_queue_line_batch = coupon_queue_id.coupon_data_queue_line_ids.filtered(
                lambda x: x.state in ["draft", "failed"])
            coupon_queue_line_batch.process_coupon_queue_line()
        return True

    def woo_action_archive(self):
        """ This method is used to call a child of the instance to active/inactive instance and its data.
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 4 November 2020 .
            Task_id: 167723
        """
        instance_obj = self.env['woo.instance.ept']
        instances = instance_obj.browse(self._context.get('active_ids'))
        for instance in instances:
            instance.woo_action_archive()

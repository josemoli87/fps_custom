import datetime
import requests
from lxml import etree

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    currency_provider = fields.Selection(selection_add=[
        ('bcv', '[VE] Central Bank of Venezuela'),
        ('bcv_usd', '[VE] USD Central Bank of Venezuela'),
        ('bcv_eur', '[VE] EUR Central Bank of Venezuela'),
    ],)

    def _parse_bcv_data(self, available_currencies):
        BCV_CURRENCIES = {'EUR': 'euro', 'CNY': 'yuan', 'TRY': 'lira', 'RUB': 'rublo', 'USD': 'dolar'}
        available_currency_names = available_currencies.mapped('name')
        request_url = 'https://www.bcv.org.ve/'

        parse_url = requests.get(request_url, timeout=30, verify=False)

        rslt = {}
        htmlelem = etree.fromstring(parse_url.content, etree.HTMLParser())
        date_elem = htmlelem.xpath("//span[hasclass('date-display-single')]")[0]
        date_rate = datetime.datetime.strptime(date_elem.get('content'), '%Y-%m-%dT%H:%M:%S-04:00').date()
        for currency_code, currency in BCV_CURRENCIES.items():
            if currency_code in available_currency_names:
                rate_elem = htmlelem.xpath(f"//div[@id='{currency}']//div[hasclass('centrado')]//strong")[0]
                rate = float(rate_elem.text.replace(',', '.')) or 1
                rslt[currency_code] = (1.0 / rate, date_rate)

        if 'VES' in available_currency_names:
            rslt['VES'] = (1.0, date_rate)

        if 'VEF' in available_currency_names:
            rslt['VEF'] = (1.0, date_rate)

        return rslt

    def _parse_bcv_usd_data(self, available_currencies):
        BCV_CURRENCIES = {'EUR': 'euro', 'CNY': 'yuan', 'TRY': 'lira', 'RUB': 'rublo',}
        available_currency_names = available_currencies.mapped('name')
        request_url = 'https://www.bcv.org.ve/'

        currencies = self.env['res.currency'].sudo().search([('name', 'in', ['VEF', 'VES']), ('active', '=', True)])
        cves = currencies.filtered(lambda x: x.name == 'VES')
        cvef = currencies.filtered(lambda x: x.name == 'VEF')

        parse_url = requests.get(request_url, timeout=30, verify=False)

        rslt = {}
        htmlelem = etree.fromstring(parse_url.content, etree.HTMLParser())
        date_elem = htmlelem.xpath("//span[hasclass('date-display-single')]")[0]
        date_rate = datetime.datetime.strptime(date_elem.get('content'), '%Y-%m-%dT%H:%M:%S-04:00').date()

        # find dolar
        rate_elem = htmlelem.xpath(f"//div[@id='dolar']//div[hasclass('centrado')]//strong")[0]
        ves_rate = float(rate_elem.text.replace(',', '.')) or 1
        rslt[cves.name] = (ves_rate, date_rate)
        rslt[cvef.name] = (ves_rate, date_rate)

        for currency_code, currency in BCV_CURRENCIES.items():
            if currency_code in available_currency_names:
                rate_elem = htmlelem.xpath(f"//div[@id='{currency}']//div[hasclass('centrado')]//strong")[0]
                rate = float(rate_elem.text.replace(',', '.')) or 1
                rslt[currency_code] = (ves_rate / rate, date_rate)

        if 'USD' in available_currency_names:
            rslt['USD'] = (1.0, date_rate)

        return rslt

    def _parse_bcv_eur_data(self, available_currencies):
        BCV_CURRENCIES = {'USD': 'dolar', 'CNY': 'yuan', 'TRY': 'lira', 'RUB': 'rublo',}
        available_currency_names = available_currencies.mapped('name')
        request_url = 'https://www.bcv.org.ve/'

        currencies = self.env['res.currency'].sudo().search([('name', 'in', ['VEF', 'VES']), ('active', '=', True)])
        cves = currencies.filtered(lambda x: x.name == 'VES')
        cvef = currencies.filtered(lambda x: x.name == 'VEF')

        parse_url = requests.get(request_url, timeout=30, verify=False)

        rslt = {}
        htmlelem = etree.fromstring(parse_url.content, etree.HTMLParser())
        date_elem = htmlelem.xpath("//span[hasclass('date-display-single')]")[0]
        date_rate = datetime.datetime.strptime(date_elem.get('content'), '%Y-%m-%dT%H:%M:%S-04:00').date()

        # find euro
        rate_elem = htmlelem.xpath(f"//div[@id='euro']//div[hasclass('centrado')]//strong")[0]
        ves_rate = float(rate_elem.text.replace(',', '.')) or 1
        rslt[cves.name] = (ves_rate, date_rate)
        rslt[cvef.name] = (ves_rate, date_rate)

        for currency_code, currency in BCV_CURRENCIES.items():
            if currency_code in available_currency_names:
                rate_elem = htmlelem.xpath(f"//div[@id='{currency}']//div[hasclass('centrado')]//strong")[0]
                rate = float(rate_elem.text.replace(',', '.')) or 1
                rslt[currency_code] = (ves_rate / rate, date_rate)

        if 'EUR' in available_currency_names:
            rslt['EUR'] = (1.0, date_rate)

        return rslt

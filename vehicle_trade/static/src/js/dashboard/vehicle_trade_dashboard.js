/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useService } from "@web/core/utils/hooks";
import { useDebounced } from "@web/core/utils/timing";
import { session } from "@web/session";
import { Domain } from "@web/core/domain";
import { sprintf } from "@web/core/utils/strings";

const { Component, useSubEnv, useState, onMounted, onWillStart, useRef } = owl;
import { loadJS, loadCSS } from "@web/core/assets"

class TradeDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.orm = useService("orm");

        this.state = useState({
            vehiclesStats: { 'total_vehicle': 0, 'available_vehicle': 0, 'in_discussion_vehicle': 0, 'sold_vehicle': 0, 'vehicle_customers': 0, 'vehicle_vendors': 0 },
            vendorBillByMonths: { 'x-axis': [], 'y-axis': [] },
            invoiceStatusGraph: { 'x-axis': [], 'y-axis': [] },
        });

        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });

        this.vendorBillByMonths = useRef('vendor_bill_by_months');
        this.invoiceStatusGraph = useRef('invoice_status_details');

        onWillStart(async () => {
            let tradeData = await this.orm.call('vehicle.trade.dashboard', 'get_vehicle_trade_dashboard', []);
            if (tradeData) {
                this.state.vehiclesStats = tradeData;
                this.state.vendorBillByMonths = { 'x-axis': tradeData['vendor_bill_month'][0], 'y-axis': tradeData['vendor_bill_month'][1] };
                this.state.invoiceStatusGraph = { 'x-axis': tradeData['invoice_status'][0], 'y-axis': tradeData['invoice_status'][1] };
            }
        });
        onMounted(() => {
            this.renderVendorBillByMonthsGraph();
            this.renderInvoiceStatusGraph();
        })
    }

    viewVehicleStatus(vehicleState) {
        let domain, context;
        let vehicles = this.getVehicleStatus(vehicleState);
        if (vehicleState === 'all') {
            domain = []
        } else {
            domain = [['status', '=', vehicleState]]
        }
        context = { 'create': false }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: vehicles,
            res_model: 'vehicle.information',
            view_mode: 'kanban',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'pivot'], [false, 'activity'], [false, 'search']],
            target: 'current',
            context: context,
            domain: domain,
        });
    }

    getVehicleStatus(vehicleState) {
        let vehicles;
        if (vehicleState === 'all') {
            vehicles = 'Total Vehicles'
        } else if (vehicleState === 'available') {
            vehicles = 'Available Vehicles'
        } else if (vehicleState === 'in_discussion') {
            vehicles = 'In Discussion Vehicles'
        } else if (vehicleState === 'sold') {
            vehicles = 'Sold Vehicles'
        }
        return vehicles;
    }

    viewVehicleVendors() {
        let domain = [['is_vendor', '=', true]];
        let context = { 'create': false }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Vendors',
            res_model: 'res.partner',
            domain: domain,
            views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'activity']],
            target: 'current',
            context: context,
        });
    }

    viewVehicleCustomers() {
        let context = { 'create': false }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Customers',
            res_model: 'res.partner',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'activity']],
            target: 'current',
            context: context,
        });
    }

    renderGraph(el, options) {
        const graphData = new ApexCharts(el, options);
        graphData.render();
    }

    renderVendorBillByMonthsGraph() {
        const options = {
            series: [{
                name: 'Total Amounts',
                data: this.state.vendorBillByMonths['y-axis'],
            }],
            chart: {
                height: 430,
                type: 'bar',
            },
            colors: ['#16db93', '#83e377', '#b9e769', '#efea5a', '#f1c453'],
            plotOptions: {
                bar: {
                    columnWidth: '30%',
                    distributed: true,
                }
            },
            dataLabels: {
                enabled: false
            },
            legend: {
                show: false
            },
            yaxis: {
                labels: {
                    formatter: function (val) {
                        return val.toFixed(0);
                    }
                },
            },
            xaxis: {
                categories: this.state.vendorBillByMonths['x-axis'],
            }
        };
        this.renderGraph(this.vendorBillByMonths.el, options);
    }

    renderInvoiceStatusGraph() {
        const options = {
            series: this.state.invoiceStatusGraph['y-axis'],
            chart: {
                type: 'pie',
                height: 430
            },
            colors: ['#2CD298', '#F2D852'],
            dataLabels: {
                enabled: false
            },
            labels: this.state.invoiceStatusGraph['x-axis'],
            legend: {
                position: 'bottom',
            },
        };
        this.renderGraph(this.invoiceStatusGraph.el, options);
    }
}
TradeDashboard.template = "vehicle_trade.trade_dashboard";
registry.category("actions").add("vehicle_trade_dashboard", TradeDashboard);
<template>
  <v-row justify="center">
    <v-dialog v-model="reprintinvoicesDialog" max-width="700px" min-width="700px">
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">Search sales invoice to reprint</span>
        </v-card-title>
        <v-container>
          <v-row class="mb-4">
            <v-text-field
              color="indigo"
              label="Invoice ID"
              background-color="white"
              hide-details
              v-model="invoice_name"
              dense
              clearable
              class="mx-4"
            ></v-text-field>
            <v-btn
              text
              class="ml-2"
              color="primary"
              dark
              @click="search_invoices"
              >Search</v-btn
            >
          </v-row>
          <v-row>
            <v-col cols="12" class="pa-1" v-if="dialog_data">
              <template>
                <v-data-table
                  :headers="headers"
                  :items="dialog_data"
                  item-key="name"
                  class="elevation-1"
                  :single-select="singleSelect"
                  show-select
                  v-model="selected"
                >
                  <template v-slot:item.grand_total="{ item }">{{
                    formtCurrency(item.grand_total)
                  }}</template>
                </v-data-table>
              </template>
            </v-col>
          </v-row>
        </v-container>
        <v-card-actions class="mt-4">
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">Close</v-btn>
          <v-btn
            v-if="selected.length"
            color="primary"
            dark
            @click="print_page"
            >Reprint</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from '../../bus';
export default {
  data: () => ({
    reprintinvoicesDialog: false,
    singleSelect: true,
    selected: [],
    dialog_data: '',
    company: '',
    invoice_name: '',
    full_invoice_name: "",
    headers: [
      {
        text: 'Customer',
        value: 'customer',
        align: 'start',
        sortable: true,
      },
      {
        text: 'Date',
        align: 'start',
        sortable: true,
        value: 'posting_date',
      },
      {
        text: 'Invoice',
        value: 'name',
        align: 'start',
        sortable: true,
      },
      {
        text: 'Amount',
        value: 'grand_total',
        align: 'start',
        sortable: false,
      },
    ],
  }),
  watch: {},
  methods: {
    close_dialog() {
      this.reprintinvoicesDialog = false;
    },
    search_invoices() {
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.search_invoices_for_reprint',
        args: {
          invoice_name: vm.invoice_name,
          company: vm.company,
        },
        async: false,
        callback: function (r) {
          if (r.message) {
            vm.dialog_data = r.message;
            vm.full_invoice_name = r.message[0].name;
          }
        },
      });
    },
    print_page() {
      const vm = this;
      vm.load_print_page();
    },

    load_print_page() {
      const url =
        frappe.urllib.get_base_url() +
        '/printview?doctype=Sales%20Invoice&name=' +
        this.full_invoice_name + 
        '&trigger_print=1' +
        '&format=' +
        'Point of Sale' +
        '&no_letterhead=' +
        '0';
      const printWindow = window.open(url, 'Print');
      printWindow.addEventListener(
        'load',
        function () {
          printWindow.print();
          // printWindow.close();
          // NOTE : uncomoent this to auto closing printing window
        },
        true
      );
    },
    formtCurrency(value) {
      value = parseFloat(value);
      return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    },
  },
  created: function () {
    evntBus.$on('open_reprint_dialog', (data) => {
    // evntBus.$on('open_invoices', () => {
      this.invoice_name = '';
      this.reprintinvoicesDialog = true;
      this.company = data;
      this.dialog_data = '';
      this.selected = [];
    });
  },
};
</script>
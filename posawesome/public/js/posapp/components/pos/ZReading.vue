<template>
  <v-row justify="center">
    <v-dialog v-model="zReading" max-width="300px">
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">Z-Reading</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-row justify="center">
              <v-col 
              cols="12"
              sm="9">
                <v-btn elevation="2" color="primary" dark @click="print_page">Print Z-Reading</v-btn>
              </v-col>
            </v-row>
            <!-- <v-row justify="center">
              <v-col 
              cols="12"
              sm="9">
                <v-text-field
                  label="Username"
                  outlined
                  clearable
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row justify="center">
              <v-col 
              cols="12"
              sm="9">
                <v-text-field
                  :append-icon="show ? 'mdi-eye' : 'mdi-eye-off'"
                  :type="show ? 'text' : 'password'"
                  label="Password"
                  @click:append="show = !show"
                  outlined
                  clearable
                ></v-text-field>
              </v-col>
            </v-row> -->
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">Close</v-btn>
          <!-- <v-btn color="primary" dark @click="submit_dialog">Submit</v-btn> -->
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from '../../bus';
export default {
  data: () => ({
    show: false,
    zReading: false,
    itemsPerPage: 20,
    dialog_data: {},
    pos_closing_shift: "POSA-CS-21-0000013",
    headers: [
      {
        text: 'Mode of Payment',
        value: 'mode_of_payment',
        align: 'start',
        sortable: true,
      },
      {
        text: 'Opening Amount',
        align: 'end',
        sortable: true,
        value: 'opening_amount',
      },
      {
        text: 'Closing Amount',
        value: 'closing_amount',
        align: 'end',
        sortable: true,
      },
      {
        text: 'Expected Amount',
        value: 'expected_amount',
        align: 'end',
        sortable: false,
      },
      {
        text: 'Difference',
        value: 'difference',
        align: 'end',
        sortable: false,
      },
    ],
    max25chars: (v) => v.length <= 20 || 'Input too long!', // TODO : should validate as number
    pagination: {},
  }),
  watch: {},
  methods: {
    close_dialog() {
      this.zReading = false;
    },

    calculate_totals() {
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.submit_total_closing_readings',
        args: {
          closing_shift:this.pos_closing_shift
        },
        async: true,
        callback: function (r) {
          //do nothing
        },
      });
    },

    print_page() {
      const vm = this;
      vm.calculate_totals();
      vm.load_print_page(); 
    },

    submit_dialog() {
      evntBus.$emit('submit_closing_pos', this.dialog_data);
      this.zReading = false;
    },
    formtCurrency(value) {
      value = parseFloat(value);
      return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    },
    load_print_page() {
      const url =
        frappe.urllib.get_base_url() +
        '/printview?doctype=POS%20Closing%20Shift&name=' +
        this.pos_closing_shift +
        '&trigger_print=1' +
        '&format=' +
        'Z Reading Report' +
        '&no_letterhead=' +
        'letter_head';
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
  },
  
  created: function () {
    evntBus.$on('open_zreading_dialog', () => {
      this.zReading = true;
    });
    // evntBus.$on('current_closing_shift', (data) => {
    //   this.pos_closing_shift = data.pos_closing_shift;
    // });
  },
};
</script>

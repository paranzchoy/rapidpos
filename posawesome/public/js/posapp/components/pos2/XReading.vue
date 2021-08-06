<template>
  <v-row justify="center">
    <v-dialog v-model="xReading" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">X-Reading</span>
        </v-card-title>
        <v-card-text>
          <h4 style="color: rgb(155, 0, 0); --darkreader-inline-color:#ff6060;" data-darkreader-inline-color="">* Head Cashier or Sales manager only   </h4>
          <v-container>
            <v-row justify="center">
              <v-col 
              cols="12">
                <v-text-field
                  label="Username"
                  v-model="inputUsername"
                  outlined
                  autocomplete="nope"
                  clearable
                  required
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row justify="center">
              <v-col 
              cols="12">
                <v-text-field
                  :append-icon="show ? 'mdi-eye' : 'mdi-eye-off'"
                  :type="show ? 'text' : 'password'"
                  label="Password"
                  v-model="inputPassword"
                  @click:append="show = !show"
                  outlined
                  autocomplete="nope"
                  clearable
                  class="input-group--focused"
                  counter
                  required
                  @keyup.enter="submit_dialog"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">Close</v-btn>
          <v-btn color="primary" dark @click="submit_dialog">Print</v-btn>
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
    xReading: false,
    itemsPerPage: 20,
    inputUsername: null,
    inputPassword: null,
    messages: '',
    dialog_data: {},
    pos_opening_shift: "",
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
      this.xReading = false;
    },

    calculate_totals() {
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.custom_posapp.submit_total_opening_readings',
        args: {
          opening_shift:this.pos_opening_shift
        },
        async: true,
        callback: function (r) {
          //do nothing
        },
      });
    },

    submit_dialog() {
      if (!this.inputUsername || !this.inputPassword) {
        evntBus.$emit("show_mesage", {
          text: `Please complete the required fields`,
          color: "warning",
        })
        return;
      } 
      else {
          const vm = this;
          frappe.call({
            method: "posawesome.posawesome.api.custom_posapp.verifyRole",
            args: {
              username: this.inputUsername,
              password: this.inputPassword
            },
            callback: function(r) {
              if(r.message) {
                 evntBus.$emit("show_mesage", {
                  text: `Please check if credentials are correct and you have necessary permissions.`,
                  color: "error",
                })
              }
              else{
                vm.load_print_page();
                vm.xReading = false;
                vm.inputUsername = null;
                vm.inputPassword = null;
              }
            }
          })
         }
    },


    formtCurrency(value) {
      value = parseFloat(value);
      return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    },

    load_print_page() {
      const url =
        frappe.urllib.get_base_url() +
        '/printview?doctype=POS%20Opening%20Shift&name=' +
        this.pos_opening_shift +
        '&trigger_print=1' +
        '&format=' +
        'X Reading Report' +
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
    evntBus.$on('open_xreading', (data) => {
      this.xReading = true;
      this.pos_opening_shift = data.name;
      this.calculate_totals();
    });
  },
};
</script>
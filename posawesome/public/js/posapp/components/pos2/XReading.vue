<template>
  <v-row justify="center">
    <v-dialog v-model="xReading" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">X-Reading</span>
        </v-card-title>
        <v-card-text>
          <span style="color: black; font-size: 15px;">*Head cashier/Sales Manager only</span>
          <v-container>
            <!-- <v-row justify="center">
              <v-col 
              cols="12"
              sm="9">
                <v-btn elevation="2" color="primary" dark @click="print_page">Print X-Reading</v-btn>
              </v-col>
            </v-row> -->
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
    // opening_shift_name: pos_opening_shift.name,
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
          //this.
        },
      });
    },

    submit_dialog() {
      
      if (!this.inputUsername || !this.inputPassword) {
        evntBus.$emit("show_mesage", {
          text: `Please complete the required fields`,
          color: "warning",
        })
      } 
      else if (this.inputUsername && this.inputPassword) {
          frappe.call({
            method: "posawesome.posawesome.api.custom_posapp.verify_password",
            args: {
              username: this.inputUsername,
              password: this.inputPassword
            },
            callback: function(r) {
              if(r.message) {
                this.messages = r.message;
              }
            }
          })
          this.load_print_page();
          this.xReading = false;
          // this.inputUsername = null;
          // this.inputPassword = null;
         } 
        //  else {
        //   evntBus.$emit("show_mesage", {
        //     text: `Username does not match. Please try again.`,
        //     color: "error",
        //   })
        // }
      
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
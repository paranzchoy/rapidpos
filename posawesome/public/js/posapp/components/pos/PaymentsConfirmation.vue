<template>
  <v-row justify="center">
    <v-dialog v-model="confirmPayment" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">Confirm Payment?</span>
        </v-card-title>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">Cancel</v-btn>
          <v-btn color="warning" dark @click="close_dialog">Add another payment</v-btn>
          <v-btn color="primary" dark @click="submit_dialog">Confirm</v-btn>
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
    confirmPayment: false,
    itemsPerPage: 20,
    inputUsername: null,
    inputPassword: null,
    messages: '',
    dialog_data: {},
    // opening_shift_name: pos_opening_shift.name,
    pos_opening_shift: "",
    max25chars: (v) => v.length <= 20 || 'Input too long!', // TODO : should validate as number
    pagination: {},
    payments:[] //this is where a list of payment transaction for a single invoice will be list at
  }),
  watch: {},
  methods: {
    close_dialog() {
      this.confirmPayment = false;
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
          this.confirmPayment = false;
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

    print_page() {
      const vm = this;
      vm.calculate_totals();
      vm.load_print_page();
    },

    formtCurrency(value) {
      value = parseFloat(value);
      return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    },

    load_print_page() {
      const url =
        frappe.urllib.get_base_url() +
        '/printview?doctype=POS%20Opening%20Shift&name=' +
        this.pos_opening_shift.name +
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

    // load_print_page() {
    //   const print_format =
    //     this.pos_profile.print_format_for_online ||
    //     this.pos_profile.print_format;
    //   const letter_head = this.pos_profile.letter_head || 0;
    //   const url =
    //     frappe.urllib.get_base_url() +
    //     '/printview?doctype=Sales%20Invoice&name=' +
    //     this.invoice_doc.name +
    //     '&trigger_print=1' +
    //     '&format=' +
    //     print_format +
    //     '&no_letterhead=' +
    //     letter_head;
    //   const printWindow = window.open(url, 'Print');
    //   printWindow.addEventListener(
    //     'load',
    //     function () {
    //       printWindow.print();
    //       // printWindow.close();
    //       // NOTE : uncomoent this to auto closing printing window
    //     },
    //     true
    //   );
    // }
  },

  created: function () {
    evntBus.$on('open_confirmation_dialog', () => {
      this.confirmPayment = true;
    });
    // evntBus.$on('current_opening_shift', (data) => {
    //   this.pos_opening_shift = data.pos_opening_shift;
    // });
  },
};
</script>
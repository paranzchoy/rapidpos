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
          <v-btn color="warning" dark @click="another_payment_dialog">Add another payment</v-btn>
          <v-btn color="primary" dark @click="submit">Confirm</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

     <v-dialog v-model="anotherPayment" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">Add a Payment?</span>
        </v-card-title>
        <v-card-actions>
          <v-btn color="error" dark @click="close_payment_dialog">Cancel</v-btn>
          <v-btn color="success" dark @click="cash_payment_dialog">Cash</v-btn>
          <v-btn color="secondary" dark @click="cc_payment_dialog">Credit Card</v-btn>
          <v-btn color="primary" dark @click="dc_payment_dialog">Debit Card</v-btn>
          <v-btn color="warning" dark @click="coupon_payment_dialog">Coupon</v-btn>
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
    anotherPayment: false,
    itemsPerPage: 20,
    inputUsername: null,
    inputPassword: null,
    messages: '',
    dialog_data: {},
    invoice_doc: '',
    pos_profile: '',
    // opening_shift_name: pos_opening_shift.name,
    pos_opening_shift: "",
    max25chars: (v) => v.length <= 20 || 'Input too long!', // TODO : should validate as number
    pagination: {}
  }),
  watch: {},
  methods: {
    close_dialog() {
      this.confirmPayment = false;
    },
    close_payment_dialog() {
      this.anotherPayment = false;
    },
    another_payment_dialog(){
      this.anotherPayment = true;
    },
    cash_payment_dialog(){
      this.close_dialog();
      this.close_payment_dialog();
      this.close_all_payment_dialog();
      evntBus.$emit('show_payment_cash', 'true');
      evntBus.$emit('another_payment_cash', this.invoice_doc);
    },
    cc_payment_dialog(){
      this.close_dialog();
      this.close_payment_dialog();
      this.close_all_payment_dialog();
      evntBus.$emit('show_payment_cc', 'true');
      evntBus.$emit('another_payment_cc', this.invoice_doc);
    },
    dc_payment_dialog(){
      this.close_dialog();
      this.close_payment_dialog();
      this.close_all_payment_dialog();
      evntBus.$emit('show_payment_dc', 'true');
      evntBus.$emit('another_payment_dc', this.invoice_doc);
    },
    coupon_payment_dialog(){
      this.close_dialog();
      this.close_payment_dialog();
      this.close_all_payment_dialog();
      evntBus.$emit('show_payment_coupon', 'true');
      evntBus.$emit('another_payment_coupon', this.invoice_doc);
    },
    close_all_payment_dialog(){
      evntBus.$emit('show_payment_cash', 'false');
      evntBus.$emit('show_payment_cc', 'false');
      evntBus.$emit('show_payment_dc', 'false');
      evntBus.$emit('show_payment_coupon', 'false');
    },
    back_to_invoice() {
      this.close_all_payment_dialog();
      evntBus.$emit('set_customer_readonly', false);
    },
    submit() {
      this.invoice_doc.payments.forEach((payment) => {
         if(payment.mode_of_payment=== "Credit Card" && payment.amount !== 0 && payment.card_number===0||payment.card_number===null){
              evntBus.$emit('show_mesage', {
              text: `Please enter card number for card transactions.`,
              color: 'error',
            });
            frappe.utils.play_sound('error');
            // this.is_credit_transaction = true;
          return;
         }
         else{
          //  this.is_credit_transaction = false;
         }
        });
      this.close_dialog();
      this.invoice_doc.payments.forEach((payment) => {
        if(payment.card_number){
          payment.card_number_hidden = payment.card_number.replace(/\d(?=\d{4})/g, "*");
        }
      });
      console.log(this.invoice_doc);
      this.submit_invoice();
      evntBus.$emit('new_invoice', 'false');
      evntBus.$emit('set_customer_default');
      this.back_to_invoice();
    },
    submit_invoice() {
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.custom_posapp.submit_invoice',
        args: {
          data: this.invoice_doc
        },
        async: true,
        callback: function (r) {
          if (r.message) {
            vm.load_print_page();
            evntBus.$emit('show_mesage', {
              text: `Invoice ${r.message.name} is Submitted`,
              color: 'success',
            });
            frappe.utils.play_sound('submit');
          }
        },
      });
    },
     load_print_page() {
      const print_format =
        this.pos_profile.print_format_for_online ||
        this.pos_profile.print_format;
      const letter_head = this.pos_profile.letter_head || 0;
      const url =
        frappe.urllib.get_base_url() +
        '/printview?doctype=Sales%20Invoice&name=' +
        this.invoice_doc.name +
        '&trigger_print=1' +
        '&format=' +
        "Sales Invoice Cash" +
        '&no_letterhead=' +
        letter_head;
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
    shortPay(e) {
      e.preventDefault();
      if (e.key === 'Backspace'){
        this.close_payment_dialog();
      }
      if (e.key === '1'){
        this.cash_payment_dialog();
      }
      if (e.key === '2'){
        this.cc_payment_dialog();
      }
       if (e.key === '3'){
        this.dc_payment_dialog();
      }
       if (e.key === '4'){
        this.coupon_payment_dialog();
      }
      
    }
  },

  created: function () {
    evntBus.$on('open_confirmation_dialog', (data) => {
      this.confirmPayment = true;
      this.invoice_doc = data;
      this.pos_profile = this.invoice_doc.pos_profile;
    });
    // evntBus.$on('current_opening_shift', (data) => {
    //   this.pos_opening_shift = data.pos_opening_shift;
    // });
    // document.addEventListener('keydown', this.shortPay.bind(this));
  },

  // destroyed() {
  //   document.removeEventListener('keydown', this.shortPay);
  // },
};
</script>
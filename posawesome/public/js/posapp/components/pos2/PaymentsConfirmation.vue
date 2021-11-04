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
          <span class="headline indigo--text">Add a Payment? (Shift + Option #)</span>
        </v-card-title>
        <v-card-actions>
          <v-btn color="error" dark @click="close_payment_dialog">Cancel (0)</v-btn>
          <v-btn color="success" dark @click="cash_payment_dialog">Cash (1)</v-btn>
          <v-btn color="secondary" dark @click="cc_payment_dialog">Credit Card (2)</v-btn>
          <v-btn color="primary" dark @click="dc_payment_dialog">Debit Card (3)</v-btn>
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
    validation_identifier: false,
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
      if (this.diff_payment === '0.00') {
        evntBus.$emit('show_mesage', {
          text: `Remaining amount balance is 0.`,
          color: 'error',
        });
        frappe.utils.play_sound('error');
        this.validation_identifier = true;
        return;
      }
      else{
        this.validation_identifier = false;
      }
      this.validate();
      if (!this.validation_identifier){
        this.anotherPayment = true;
      }
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
    close_all_payment_dialog(){
      evntBus.$emit('show_payment_cash', 'false');
      evntBus.$emit('show_payment_cc', 'false');
      evntBus.$emit('show_payment_dc', 'false');
    },
    back_to_invoice() {
      this.close_all_payment_dialog();
      evntBus.$emit('set_customer_readonly', false);
    },
    submit() {
      this.validate();
      if (!this.pos_profile.posa_allow_partial_payment && this.total_payments < this.invoice_doc.grand_total && !this.invoice_doc.is_credit_sale) {
        evntBus.$emit('show_mesage', {
          text: `The amount paid is not complete`,
          color: 'error',
        });
        frappe.utils.play_sound('error');
        this.validation_identifier = true;
        return;
      }      
      if(!this.validation_identifier){
        this.close_dialog();
        this.invoice_doc.payments.forEach((payment) => {
          if(payment.card_number){
            payment.card_number_hidden = payment.card_number.replace(/\d(?=\d{4})/g, "*");
          }
        });
        this.submit_invoice();
        evntBus.$emit('new_invoice', 'false');
        evntBus.$emit('set_customer_default');
        this.back_to_invoice();
      }
      
    },
    validate(){
        this.invoice_doc.payments.forEach((payment) => {
        if(payment.mode_of_payment === 'Credit Card' && payment.amount !== 0){
            if(payment.card_number==='0'||payment.card_number==null){
                evntBus.$emit('show_mesage', {
                  text: `Please enter card number for card transactions.`,
                  color: 'error',
                });
                frappe.utils.play_sound('error');
                this.validation_identifier = true;
                return;
            }
            else if(payment.approval_code==null || payment.card_expiry_date==null || payment.bank_name == null){
                evntBus.$emit('show_mesage', {
                  text: `Please complete the form before submitting.`,
                  color: 'error',
                });
                frappe.utils.play_sound('error');
                this.validation_identifier = true;
                return;
            }
            else if (payment.card_number.length > 16){
              evntBus.$emit('show_mesage', {
              text: `Card Number can't exceed 16 numbers.`,
              color: 'error',
              });
              frappe.utils.play_sound('error');
              this.validation_identifier = true;
              return;
            }
            else{
                this.validation_identifier = false;
            }
        }
        else if(payment.mode_of_payment === 'Debit Card' && payment.amount !== 0) {
          if(payment.bank_name == null){
               evntBus.$emit('show_mesage', {
                  text: `Please input bank name.`,
                  color: 'error',
                });
                frappe.utils.play_sound('error');
                this.validation_identifier = true;
                return;
          }
          else{
                this.validation_identifier = false;
          }
        }
      });

      if (!this.invoice_doc.is_return && this.total_payments < 0) {
        evntBus.$emit('show_mesage', {
          text: `Payments not correct`,
          color: 'error',
        });
        frappe.utils.play_sound('error');
        this.validation_identifier = true;
        return;
      }
      if (
        this.pos_profile.posa_allow_partial_payment &&
        !this.pos_profile.posa_allow_credit_sale &&
        this.total_payments == 0
      ) {
        evntBus.$emit('show_mesage', {
          text: `Please enter the amount paid`,
          color: 'error',
        });
        frappe.utils.play_sound('error');
        this.validation_identifier = true;
        return;
      }

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
        "Jacobs Breadnuts Receipt" +
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
    shortCancelPay(e){
      if (e.key === '0' && e.ctrlKey){
        e.preventDefault();
        this.close_payment_dialog();
      }
    },
    shortCashPay(e){
      if (e.key === '=' && e.ctrlKey){
        e.preventDefault();
        this.cash_payment_dialog();
      }
    },
    shortCreditCardPay(e){
      if (e.key === '-' && e.ctrlKey){
        e.preventDefault();
        this.cc_payment_dialog();
      }
    },
    shortDebitCardPay(e){
      if (e.key === ']' && e.ctrlKey)
        e.preventDefault();
        this.dc_payment_dialog();
      }
    },
  computed:{
    total_payments() {
      let total = flt(this.invoice_doc.loyalty_amount);
      this.invoice_doc.payments.forEach((payment) => {
        total += flt(payment.amount);
      });
      return total.toFixed(2);
    },
    diff_payment() {
      return (this.invoice_doc.grand_total - this.total_payments).toFixed(2);
    }
  },

  created () {
    evntBus.$on('open_confirmation_dialog', (data) => {
      this.confirmPayment = true;
      this.invoice_doc = data;
      this.pos_profile = this.invoice_doc.pos_profile;
    });
    evntBus.$on('register_pos_profile', (data) => {
        this.pos_profile = data.pos_profile;
    });
    // document.addEventListener('keydown', this.shortCancelPay.bind(this));
    // document.addEventListener('keydown', this.shortCashPay.bind(this));
    // document.addEventListener('keydown', this.shortCreditCardPay.bind(this));
    // document.addEventListener('keydown', this.shortDebitCardPay.bind(this));
  },

  // destroyed() {
  //   document.removeEventListener('keydown', this.shortCancelPay);
  //   document.removeEventListener('keydown', this.shortCashPay);
  //   document.removeEventListener('keydown', this.shortCreditCardPay);
  //   document.removeEventListener('keydown', this.shortDebitCardPay);
  // },
};
</script>
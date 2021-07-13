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
          <v-btn color="primary" dark @click="submit_dialog">Confirm</v-btn>
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
          <v-btn color="success" dark @click="close_payment_dialog">Cash</v-btn>
          <v-btn color="primary" dark @click="close_payment_dialog">Debit Card</v-btn>
          <v-btn color="secondary" dark @click="close_payment_dialog">Credit Card</v-btn>
          <v-btn color="warning" dark @click="close_payment_dialog">Coupon</v-btn>
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
    close_payment_dialog() {
      this.anotherPayment = false;
    },
    another_payment_dialog(){
      this.anotherPayment = true;
    },
    back_to_invoice() {
      evntBus.$emit('show_payment', 'false');
      evntBus.$emit('set_customer_readonly', false);
    },
    submit() {
      this.submit_invoice();
      evntBus.$emit('new_invoice', 'false');
      this.back_to_invoice();
      this.card_number = '';

    },
    submit_invoice() {
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.submit_invoice',
        args: {
          data: this.invoice_doc,
          cardNumber: this.card_number,
          cardNumberHid: this.card_number.replace(/\d(?=\d{4})/g,"*")
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
    }
  },

  created: function () {
    evntBus.$on('open_confirmation_dialog', (data) => {
      this.confirmPayment = true;
      this.invoice_doc = data;
    });
    // evntBus.$on('current_opening_shift', (data) => {
    //   this.pos_opening_shift = data.pos_opening_shift;
    // });
  },
};
</script>
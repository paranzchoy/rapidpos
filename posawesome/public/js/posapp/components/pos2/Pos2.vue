<template>
  <div fluid>
    <EnabledDiscount></EnabledDiscount>
    <ClosingDialog></ClosingDialog>
    <CashWithdrawal></CashWithdrawal>
    <ResumeUser></ResumeUser>
    <ReprintInvoice></ReprintInvoice>
    <XReading></XReading>
    <ZReading></ZReading>
    <Help></Help>
    <PaymentsConfirmation></PaymentsConfirmation>
    <ClosePosShift></ClosePosShift>
    <Drafts></Drafts>
    <Returns></Returns>
    <NewCustomer></NewCustomer>
    <OpeningDialog v-if="dialog" :dialog="dialog"></OpeningDialog>
    <v-row v-show="!dialog">
      <v-col v-show="!payment&&!payment_cash&&!payment_credit_card&&!payment_debit_card&&!payment_coupon" xl="5" lg="6" md="6" sm="6" cols="12" class="pos pr-0">
      <!-- <v-col v-show="!payment" xl="5" lg="6" md="6" sm="6" cols="12" class="pos pr-0"> -->
        <ItemsSelector></ItemsSelector>
      </v-col>
      <v-col v-show="payment" xl="5" lg="6" md="6" sm="6" cols="12" class="pos pr-0">
        <Payments></Payments>
      </v-col>
       <v-col v-show="payment_cash" xl="5" lg="6" md="6" sm="6" cols="12" class="pos pr-0">
        <PaymentsCash></PaymentsCash>
      </v-col>
      <v-col v-show="payment_credit_card" xl="5" lg="6" md="6" sm="6" cols="12" class="pos pr-0">
        <PaymentsCreditCard></PaymentsCreditCard>
      </v-col>
      <v-col v-show="payment_debit_card" xl="5" lg="6" md="6" sm="6" cols="12" class="pos pr-0">
        <PaymentsDebitCard></PaymentsDebitCard>
      </v-col>
      <v-col v-show="payment_coupon" xl="5" lg="6" md="6" sm="6" cols="12" class="pos pr-0">
        <PaymentsCoupon></PaymentsCoupon>
      </v-col>
      <v-col xl="7" lg="6" md="6" sm="6" cols="12" class="pos">
        <Invoice></Invoice>
      </v-col>
    </v-row>
  </div>
</template>


<script>
//Original POSAwesome components
import { evntBus } from "../../bus";
import ItemsSelector from "../pos/ItemsSelector.vue";
// import Payments from "../pos/Payments.vue";
import Drafts from "../pos/Drafts.vue";
import ClosingDialog from "../pos/ClosingDialog.vue";
import Returns from "../pos/Returns.vue";

//Custom POSAwesome components
import OpeningDialog from "./OpeningDialog.vue";
import PaymentsConfirmation from "./PaymentsConfirmation.vue";
import ClosePosShift from "./ClosePosShift2.vue";
import Payments from "./Payments.vue";
// import ClosePosShift from "./ClosePosShift.vue";
import Help from "./Help.vue";
import PaymentsCash from "./PaymentsCash.vue";
import PaymentsCreditCard from "./PaymentsCreditCard.vue";
import PaymentsDebitCard from "./PaymentsDebitCard.vue";
import PaymentsCoupon from "./PaymentsCoupon.vue";
import CashWithdrawal from "./CashWithdrawal.vue";
import ResumeUser from "./ResumeUser.vue";
import ReprintInvoice from "./ReprintInvoice.vue";
import XReading from "./XReading.vue";
import ZReading from "./ZReading.vue";
import Invoice from "./Invoice.vue";
import EnabledDiscount from "./EnableDiscount.vue";
import NewCustomer from "./NewCustomer.vue";

export default {
  data: function () {
    return {
      dialog: false,
      pos_profile: "",
      pos_opening_shift: "",
      pos_closing_shift: "",
      item_selector: true,
      payment: false,
      timerCount: 0,
      payment_cash: false,
      payment_debit_card: false,
      payment_credit_card: false,
      payment_coupon: false
    };
  },

  components: {
    ItemsSelector,
    OpeningDialog,
    Payments,
    PaymentsConfirmation,
    Drafts,
    ClosingDialog,
    ClosePosShift,
    NewCustomer,
    Returns,
    Help,
    CashWithdrawal,
    ResumeUser,
    ReprintInvoice,
    XReading,
    ZReading,
    PaymentsCash,
    PaymentsCreditCard,
    PaymentsDebitCard,
    PaymentsCoupon,
    CashWithdrawal,
    Invoice,
    EnabledDiscount
  },

  watch: {
      timerCount: {
                  handler(value) {

                      if (value < 10) {
                          setTimeout(() => {
                              this.timerCount++;
                          }, 1000);
                      } 
                      // else {
                      //     // this.get_idle_data();
                      // }
                      // if (value == 10) {
                      //   this.idleDialog = true;
                      // }

                  },
                  immediate: true // This ensures the watcher is triggered upon creation
              }
    },

  methods: {
    
    resetTimerCount() {
    // this.timerCount = 0;
      clearTimeout(this.timerCount);
    },

    check_opening_entry() {
      return frappe
        .call("posawesome.posawesome.api.posapp.check_opening_shift", {
          user: frappe.session.user,
        })
        .then((r) => {
          if (r.message) {
            this.pos_profile = r.message.pos_profile;
            this.pos_opening_shift = r.message.pos_opening_shift;
            evntBus.$emit("register_pos_profile", r.message);
            evntBus.$emit("set_company", r.message.company);
            console.log("LoadPosProfile");
          } else {
            this.create_opening_voucher();
          }
        });
    },
    create_opening_voucher() {
      this.dialog = true;
    },
     get_closing_data() {
      return frappe
        .call("posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.make_closing_shift_from_opening", {
          opening_shift: this.pos_opening_shift,
        })
        .then((r) => {
          if (r.message) {
            evntBus.$emit("open_ClosingDialog",r.message);
          } else {
            console.log(r)
          }
        });
    },
    get_closing_data2() {
      return frappe
        .call("posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.make_closing_shift_from_opening", {
          opening_shift: this.pos_opening_shift,
        })
        .then((r) => {
          if (r.message) {
            evntBus.$emit("open_ClosingDialog2",r.message);
          } else {
            console.log(r)
          }
        });
    },
    // get_withdrawal_data() {
    //   evntBus.$emit('open_withdrawal', this.pos_opening_shift);
    // },
    submit_closing_pos(data){
      frappe
        .call("posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.submit_closing_shift", {
          closing_shift: data,
        })
        .then((r) => {
          if (r.message) {
            this.pos_closing_shift = r.message.pos_closing_shift;
            evntBus.$emit("current_closing_shift", r.message);
            evntBus.$emit("show_mesage", {
              text: `POS Shift Closed`,
              color: "success",
            });
            this.check_opening_entry();
          } else {
            console.log(r)
          }
        });
    },
     print_page() {
      const vm = this;
      vm.load_print_page();
    },

    load_print_page() {
      const url =
        frappe.urllib.get_base_url() +
        '/printview?doctype=POS%20Closing%20Shift&name=' +
        this.pos_closing_shift.name +
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
    this.$nextTick(function () {
      this.check_opening_entry();
      evntBus.$on("close_opening_dialog", () => {
        this.dialog = false;
      });
      evntBus.$on("register_pos_data", (data) => {
        this.pos_profile = data.pos_profile;
        this.pos_opening_shift = data.pos_opening_shift;
        evntBus.$emit("register_pos_profile", data);
        console.log("LoadPosProfile");
      });
      evntBus.$on("show_payment", (data) => {
        this.payment = true ? data ==="true": false;
        this.item_selector = false;
        // evntBus.$emit("update_cur_items_details");
      })
      
        //** FOR DIFFERENT PAYMENT METHOD PURPOSES**/
      evntBus.$on("show_payment_cash", (data) => {
        this.payment_cash = true ? data ==="true": false;
      })
      evntBus.$on("show_payment_cc", (data) => {
        this.payment_credit_card = true ? data ==="true": false;
      })
      evntBus.$on("show_payment_dc", (data) => {
        this.payment_debit_card = true ? data ==="true": false;
      })
      evntBus.$on("show_payment_coupon", (data) => {
        this.payment_coupon = true ? data ==="true": false;
      })

      evntBus.$on("open_closing_dialog", () => {
        this.get_closing_data()
      })
      evntBus.$on("open_closing_dialog2", () => {
        this.get_closing_data2()
      })
      evntBus.$on("open_withdrawal_2", () => {
        // this.get_withdrawal_data()
        evntBus.$emit('open_withdrawal', this.pos_opening_shift);
      })
      evntBus.$on("open_xreading_dialog", () => {
        evntBus.$emit('open_xreading', this.pos_opening_shift);
      })
      evntBus.$on("submit_closing_pos", (data) => {
        this.submit_closing_pos(data)
      })
    });
  },
};
</script> 

<style scoped>
</style>
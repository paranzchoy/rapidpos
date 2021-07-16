<template>
  <v-row justify="center">
    <!-- Verify username & password -->
    <v-dialog v-model="verify_user" max-width="550px">
      <v-card>
        <!-- Title -->
        <v-card-title>
          <span>Withdrawal</span>
          <v-spacer></v-spacer>
        </v-card-title>
        
        <!-- Username -->
        <v-row justify="center">
          <h4 style="color: rgb(155, 0, 0); --darkreader-inline-color:#ff6060;" data-darkreader-inline-color="">* Head Cashier or Sales manager only   </h4>
          <v-col cols="12" sm="7" >
            <v-text-field label="Username" v-model="inputUsername" clearable required ></v-text-field>
          </v-col>
        </v-row>

        <!-- Password -->
        <v-row justify="center">
          <v-col cols="12" sm="7" >
              <v-text-field
                :append-icon="show ? 'mdi-eye' : 'mdi-eye-off'"
                :type="show ? 'text' : 'password'"
                name="input-10-2"
                label="Password"
                v-model="inputPassword"
                value=""
                class="input-group--focused"
                @click:append="show = !show"
                clearable
                counter
                required
                @keyup.enter="submit_dialog"
              ></v-text-field>
          </v-col>
        </v-row>

        <!-- Buttons -->
        <v-card-actions>
          <v-spacer></v-spacer>
            <v-btn color="error" dark @click="close_login_dialog">Cancel</v-btn>
            <v-btn color="primary" @click="configure_modal">Start</v-btn>
          </v-card-actions>
        </v-card>
     </v-dialog>

    <!-- Tabs: Cash, Cards, Coupon-->
   <v-dialog v-model="withdrawalDialog" max-width="900px">
        <v-card>
        <!-- Title -->
        <v-card-title>
          <span class="headline indigo--text">Withdrawal</span>
        </v-card-title>

        <!-- Content -->
        <v-card-text>
          <template>
            <form>
            <!-- Tab titles -->
            <div class="tabs">
                <a v-on:click="activetab='tabCash'" v-bind:class="[ activetab === 'tabCash' ? 'active' : '' ]">Cash</a>
                <a v-on:click="activetab='tabCard'" v-bind:class="[ activetab === 'tabCard' ? 'active' : '' ]" @click="get_card_invoices()">Card</a>
                <a v-on:click="activetab='tabCoupon'" v-bind:class="[ activetab === 'tabCoupon' ? 'active' : '' ]" @click="get_coupons_invoices()">Coupon</a>
            </div>
            <div class="content">
              <!-- TAB: Cash -->
              <div v-if="activetab ==='tabCash'" class="tabcontent2">
                <template> 
                  <v-data-table
                    :headers="denomHeaders"
                    :items="denominations"
                    :items-per-page="5"
                    class="elevation-1"
                    hide-default-footer 
                    disable-pagination
                    dense
                    height="320px"  
                  >
                  
                  <template v-slot:item.quantity="props">
                    <v-row justify="center">
                      <v-col
                        sm="7"
                      >
                      <v-text-field
                          v-model="cash_withdrawal.cash_details = props.item.quantity"
                          :rules="[max25chars]"
                          label="Edit"
                          single-line
                          type="number"
                          dense
                          min=0 oninput="validity.valid||(value='');"
                      ></v-text-field>
                      </v-col>
                    </v-row>
                  </template>
                  <template  v-slot:item.total="{ item }">{{
                    (item.total = 
                        item.amount * item.quantity
                    )
                    }}
                  </template>
                  </v-data-table>
                  <template>
                    <v-row justify="end">
                      <v-col
                        cols="12"
                        sm="7"
                        >
                      </v-col>
                      <v-col
                        cols="12"
                        sm="3"
                        >
                        <v-subheader>Cash Total:</v-subheader>
                      </v-col>
                      <v-col
                        cols="12"
                        sm="2"
                        class="text-right"
                      >
                      <v-text-field 
                          v-model="cash_withdrawal.cash_amount = totalAmount"
                          single-line
                          type="number"
                          readonly
                          label="Cash"
                          dense
                      ></v-text-field>
                      </v-col>
                    </v-row>
                  </template>
                  <!-- <v-text-field 
                      v-model="cash_withdrawal.cash_amount = totalAmount"
                      single-line
                      type="number"
                      readonly
                      label="Cash"
                  ></v-text-field> -->
                </template>
              </div>

        

              <!-- TAB: Card -->
              <div v-if="activetab ==='tabCard'" class="tabcontent">
                <template>
                  <v-data-table
                    v-model="cash_withdrawal.card_details"
                    :headers="headers"
                    :items="card_invoices"
                    :single-select="singleSelect"
                    item-key="name"
                    show-select
                    class="elevation-1"
                    height="320px"
                  >
                  </v-data-table>
                </template>
              </div>

              <!-- TAB COUPON -->
              <div v-if="activetab ==='tabCoupon'" class="tabcontent">
                <template>
                  <v-data-table
                    v-model="cash_withdrawal.coupon_details"
                    :headers="coupon_header"
                    :items="coupon_list"
                    :single-select="singleSelect"
                    item-key="name"
                    show-select
                    class="elevation-1"
                    height="320px"
                  >
                  </v-data-table>
                </template>
              </div>
            </div>
            </form>
          </template>
        </v-card-text>


      




        <!-- Total summary -->
        <!-- <template>
          <v-row justify="end" dense>
            <v-col
              cols="12"
              sm="3"
              class="text-right"
              style="left: -35px; top: -16px; transition: none 0s ease 0s; cursor: move;"
            >
            <v-text-field 
                v-model="cash_withdrawal.cash_amount = totalAmount"
                single-line
                type="number"
                readonly
            ></v-text-field>
            </v-col>

            <v-col
              cols="12"
              sm="3"
              class="text-right"
              style="left: -35px; top: -16px; transition: none 0s ease 0s; cursor: move;"
            >
            <v-text-field 
                :value="formtSumCardInvoices(this.total_card_amount)"
                single-line
                readonly
            ></v-text-field>
            </v-col>

            <v-col
              cols="12"
              sm="3"
              class="text-right"
              style="left: -35px; top: -16px; transition: none 0s ease 0s; cursor: move;"
            >
            <v-text-field 
                single-line
                type="number"
                readonly
            ></v-text-field>
            </v-col>
          </v-row>
        </template> -->

        <template>
          <v-row no-gutters class="ml-5 mr-5 pa-0" style="height: 0%; margin-left: 5px;">
            <v-col cols="4">
              <v-text-field
                v-model="cash_withdrawal.cash_amount = totalAmount"
                label="Cash"
                outlined
                dense
                readonly
                hide-details
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <v-text-field
                :value="formtSumCardInvoices(this.total_card_amount)"
                label="Card"
                outlined
                dense
                readonly
                hide-details
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <v-text-field
                :value="formtSumCoupon(this.total_coupon_amount)"
                label="Coupon"
                outlined
                dense
                readonly
                hide-details
              ></v-text-field>
            </v-col>
            <!-- <v-col cols="3">
              <v-text-field
                v-model="total_denom_amount = TotalDenomAmount"
                label="TOTAL"
                outlined
                dense
                readonly
                hide-details
              ></v-text-field>
            </v-col> -->
          </v-row> 
        </template>
        <br>
        <template>
          <div>
          <v-row no-gutters class="ml-5 mr-5 pa-0" style="height: 0%; margin-left: 5px;">
            <v-col cols="4">
              <v-text-field
                v-model="cash_withdrawal.total_withdrawal_amount = TotalDenomAmount"
                label="Total Amount"
                readonly
                hide-details
              ></v-text-field>
            </v-col>
          </v-row>
          </div>
        </template>

        <!-- Buttons -->
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_withdrawal_dialog">Close</v-btn>
          <v-btn color="primary" dark @click="submit_dialog2">Submit</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from "../../bus";
export default {
  // props: ["draftsDialog"],
  data: () => ({
    length: 0,
    couponTable: null,
    activetab: 'tabCash',
    el: '#tabs',
    valid: true,
    withdrawalDialog: false,
    dialog2: false,
    verify_user: false,
    show: false,
    verify: true,
    cash_amount: "",
    total_withdrawal_amount: "",
    cash_withdrawal: {},
    cash_details: "",
    name:"",
    denominations: [],
    cash_details_push: [],
    denomHeaders: [
      {
        text: 'DENOMINATION',
        align: 'end',
        sortable: false,
        value: 'amount',
        width: '25%',
      },
      {
        text: 'QTY',
        align: 'center',
        sortable: false,
        value: 'quantity',
        width: '50%',
      },
       {
        text: 'Total',
        align: 'end',
        sortable: false,
        value: 'total',
        width: '25%',
      },
    ],
    max25chars: (v) => v.length <= 20 || 'Input too long!', // TODO : should validate as number
    pagination: {},
    comment: "",
    valid: false,
    type: null,
    items: [
      'Cash',
      'Card',
    ],
    user: frappe.session.user,
    role: "Head Cashier",
    inputUsername: null,
    inputPassword: null,
    card_invoices: [],
    selected_card_invoices: [],
    singleSelect: false,
    headers: [{text:'Card Type', value:'mode_of_payment'}, {text:'Card #', value:'card_number_hidden'},{text:'Invoice', value:'name'}, {text:'Amount', value:'amount'}],
    total_card_amount: 0,
    total_coupon_amount: 0,
    total_denom_amount: 0,
    isTesting: true,                                      /** SET TO FALSE FOR PRODUCTION **/
    cash_withdrawal_name:'',


    // COUPON DATA
    coupon_list:[],
    singleSelect: false,
    coupon_header: [{text:'Coupon #', value:''},{text:'Description', value:''},{text:'Amount', value:'amount'}],
    
  }),
  watch: {

     length (val) {
      this.couponTable = val - 1
    },

  },
  methods: {
    close_login_dialog() {
      // Reset the Form
      this.inputUsername = null
      this.inputPassword = null

      // Close Dialog
      this.verify_user = false;

      
    },
    close_withdrawal_dialog() {
      // Reset the Form
       this.denominations.forEach((element) => {
        element.quantity = "0"
      })
      this.cash_withdrawal.card_details = []
      this.cash_withdrawal.coupon_details = []

      // Close Dialog
      this.withdrawalDialog = false;
      
    },
    get_denominations() {
      const vm = this;
        frappe.call({
          method: "posawesome.posawesome.api.custom_posapp.get_denominations",
           callback: function (r) {
          if (r.message) {
            r.message.get_denom.forEach((element) => {
              vm.denominations.push(element)
            })
          }
        },
        });
    },
    get_card_invoices(){
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.custom_posapp.get_card_invoices',
        args: {
          opening_shift: vm.cash_withdrawal.posa_opening_shift
        },
        async: true,
        callback: function (r) {
          if (r.message) {
            r.message.forEach((element) => {
              if(!vm.card_invoices.some(i => i.name === element.name))
              {
                vm.card_invoices.push(element);
              }
            })
          }
        },
      });
   },


    // GET COUPON LIST
   get_coupons_invoices(){
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.custom_posapp.get_coupons_invoices',
        args: {
          opening_shift: vm.cash_withdrawal.posa_opening_shift
        },
        async: true,
        callback: function (r) {
          if (r.message) {
            r.message.forEach((element) => {
              if(!vm.coupon_list.some(i => i.name === element.name))
              {
                vm.coupon_list.push(element);
              }
            })
          }
        },
      });
   },

//TEST COMMI
    // CASH_DETAILS METHOD
    cashDetailsMethod(){
      this.denominations.forEach((element) => {
        if(element.quantity!=0){
         this.cash_details_push.push(element);
        }
      })
        

    },


      // COUPON_DETAILS METHOD
     couponDetailsMethod() {
      this.coupon_list.push( this.coupon_data );
    },

    formtSumCardInvoices(value) {
      // const vm = this;
      value = parseFloat(value);
      if(this.cash_withdrawal.card_details!=null){
         this.cash_withdrawal.card_details.forEach((element) => {
          value = value + element.amount;
         })
        // this.total_card_amount = value;
      }
      return value;
      // return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');;
    },

    formtSumCoupon(value) {
      // const vm = this;
      value = parseFloat(value);
      if(this.cash_withdrawal.coupon_details!=null){
         this.cash_withdrawal.coupon_details.forEach((element) => {
          value = value + element.amount;
         })
        // this.total_card_amount = value;
      }
      return value;
      // return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');;
    },
  configure_modal() {
      // const checks = this.role;
      // var check_role = checks.includes("Head Cashier");

      // Validation
      if (!this.inputUsername || !this.inputPassword && this.role) {
        evntBus.$emit("show_mesage", {
          text: `Please complete the required fields`,
          color: "warning",
        })
      }
       
      else {    
        if (this.inputUsername && this.inputPassword && this.role) {
          frappe.call({
            method: "posawesome.posawesome.api.custom_posapp.verify_user",
            args: {
              username: this.inputUsername,
              password: this.inputPassword,
              role: this.role
            },
            callback: function(r) {
              if(!r.exc) {
                callback();
              }
            }
          })

          this.withdrawalDialog = true;
          this.verify_user = false;
          this.inputUsername = null;
          this.inputPassword = null;
         } else {
          evntBus.$emit("show_mesage", {
            text: `Username does not match. Please try again.`,
            color: "error",
          })
        }
      }
      this.$refs.form.reset()

    },
    submit_dialog() {
      if (this.cash_amount) {
        const vm = this;
        const args = {
            name: this.name,
            cash_amount: this.cash_amount,
            cash_details: this.cash_details,
            card_amount: this.formtSumCardInvoices(this.total_card_amount),       
        };

        frappe.call({
          method: "posawesome.posawesome.api.custom_posapp.create_withdrawal_test",
          args: args,
          callback: (r) => {
              evntBus.$emit("show_mesage", {
                text: "Withdrawal created successfully.",
                color: "success",
              });
          },
        });

      }
      this.withdrawalDialog = false;
    },
      submit_dialog2(){
      this.cashDetailsMethod();
      this.couponDetailsMethod();
      this.cash_withdrawal.cash_details = this.cash_details_push;
      this.cash_withdrawal.card_amount = this.formtSumCardInvoices(this.total_card_amount);
      // this.cash_withdrawal.coupon = this.formtSumCoupon(this.total_coupon_amount);
      const cash_withdrawal_temp = this.cash_withdrawal;
      console.log({cash_withdrawal_temp});

      frappe
        .call("rapidposcustom.rapidposcustom.api.rapidposcustom.submit_pos_opening_shift_withdrawal2", {
          withdrawal: this.cash_withdrawal,
        })
        .then((r) => {
          if (r.message) {
            this.cash_withdrawal_name = r.message;
            this.load_print_page();
            evntBus.$emit("show_mesage", {
              text: `Withdrawal created successfully.`,
              color: "success",
            });
            this.cash_details_push = []
          } else {
            console.log(r)
          }
        });
      
       // Reset the Form
       this.denominations.forEach((element) => {
        element.quantity = "0"
      })
      this.cash_withdrawal.card_details = []
      this.cash_withdrawal.coupon_details = []

      // Close Dialog
      this.withdrawalDialog = false;
    


    },    
    formtCurrency(value) {
      value = parseFloat(value);
      return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    },
    load_print_page() {
      const url =
        frappe.urllib.get_base_url() +
        '/printview?doctype=POS%20Opening%20Shift%20Withdrawal%20Details&name=' +
        this.cash_withdrawal_name +
        '&trigger_print=1' +
        '&format=' +
        'Cash Withdrawal Report' +
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
    }
  },

 
  created: function () {
    evntBus.$on("open_withdrawal", (data) => {
      if(this.isTesting) {
        this.withdrawalDialog = false;
        this.verify_user = true;
      } else {
        this.verify_user = false;
      }

      this.cash_withdrawal.posa_opening_shift = data.name
    });

    this.$nextTick(function (){
      this.get_denominations();
    });

  },
  computed: {
    totalAmount: function(){

      return this.denominations.reduce(function(totalSum, item){

        return totalSum + (item.amount * item.quantity);
      },0);
    },
    TotalDenomAmount: function(){

      return this.totalAmount + this.formtSumCardInvoices(this.total_card_amount) + this.formtSumCoupon(this.total_coupon_amount);
     
    },
  }
};
</script>

<style lang="scss">
/* Import Google Font */
@import url(https://fonts.googleapis.com/css?family=Nunito+Sans);

/* Style the tabs */
.tabs {
    overflow: hidden;
    margin-bottom: -2px; /* hide bottom border */
    margin-left: 24px;
}

.tabs a{
    float: left;
    cursor: pointer;
    padding: 12px 24px;
    transition: background-color 0.2s;
    border: 1px solid #ccc;
    border-right: none;
    background-color: #f1f1f1;
    border-radius: 10px 10px 0 0;
    font-weight: bold;
}
.tabs a:last-child { 
    border-right: 1px solid #ccc;
}

/* Change background color of tabs on hover */
.tabs a:hover {
    background-color: #aaa;
    color: #fff;
}

/* Styling for active tab */
.tabs a.active {
    background-color: #fff;
    color: #484848;
    border-bottom: 2px solid #fff;
    cursor: default;
}

/* Style the tab content */
.tabcontent {
    padding: 30px 50px;
    border: 1px solid #ccc;
    border-radius: 10px;
    box-shadow: 4px 4px 8px #e1e1e1
}

.tabcontent2 {
    padding: 30px 90px 0px 90px;
    border: 1px solid #ccc;
    border-radius: 10px;
    box-shadow: 4px 4px 8px #e1e1e1
}

.right-input input {
  text-align: right
}

.tabcontent td {
  padding: 0.3em 0.4em;
  color: #484848;
}
.tabcontent td.legend { 
  color: #888; 
  font-weight: bold;
  text-align: right;
}
.tabcontent .map {
  height: 173px;
  width: 220px;
  background: #D3EAFB;
  margin-left: 60px;
  border: 1px solid #ccc;
  border-radius: 10px;
}
.data { width: 120px; }
</style>

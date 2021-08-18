<template>

  <!------------------ Verify username & password ------------------>

  <v-row justify="center">
    <v-dialog v-model="verify_user" max-width="500px">
      <v-card>
        <v-card-title>
          <span>POS Closing Shift</span>
          <v-spacer></v-spacer>
        </v-card-title>

        <v-row justify="center">
          <h4 style="color: rgb(155, 0, 0); --darkreader-inline-color:#ff6060;" data-darkreader-inline-color="">* Head Cashier or Sales manager only   </h4>
            <v-col cols="12" sm="7">
                <v-text-field
                    label="Username"
                    v-model="inputUsername"
                    clearable
                    required
                    @keyup.enter="configure_modal"
                  >
                </v-text-field>
            </v-col>  
        </v-row>

        <v-row justify="center">
          <v-col cols="12" sm="7">
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
              @keyup.enter="configure_modal"
            ></v-text-field>
          </v-col>
        </v-row>

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn color="error" dark @click="close_verify_user">Cancel</v-btn>

          <v-btn color="primary" @click="configure_modal">Verify</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

<!----------------------------- Close POS Shift --------------------------->
  
    <v-dialog v-model="closingShiftDialog" max-width="900px">

      <v-card>
        
        <v-card-title>
          <span class="headline indigo--text">Closing POS Shift</span>
        </v-card-title>

        <v-card-text>
          <template>
            <div class="tabs">
                <a v-on:click="activetab='1'" v-bind:class="[ activetab === '1' ? 'active' : '' ]">Details</a>
                <a v-on:click="activetab='2'" v-bind:class="[ activetab === '2' ? 'active' : '' ]">Cash</a>
            </div>
            <div class="content">
                <div v-if="activetab ==='1'" class="tabcontent">
                  <template>
                        <v-simple-table
                          fixed-header
                          height="300px"
                        >
                            <template v-slot:default>
                                <thead>
                                  <tr>
                                    <th class="text-left">
                                      Name
                                    </th>
                                    <th class="text-left">
                                      Value
                                    </th>
                                  </tr>
                                </thead>
                                <tbody>
                                  <tr
                                    v-for="item in sample_items"
                                    :key="item.name">
                                    <td>{{ item.name }}</td>
                                    <td>{{ item.value }}</td>
                                  </tr>
                                </tbody>
                            </template>
                        </v-simple-table>
                  </template>
                </div>
                <div v-if="activetab ==='2'" class="tabcontent2">
                    <template>
                        <div>
                           <v-data-table
                            dense
                            :headers="denomHeaders"
                            :items="denominations"
                            :items-per-page="5"
                            class="elevation-1"
                            hide-default-footer 
                            disable-pagination
                            v-model="pos_closing_shift_data.cash_details"
                            height="373px"
                            >
                              <template v-slot:item.quantity="props">
                                <v-col sm="7">
                                  <v-text-field
                                      v-model="pos_closing_shift_data.cash_details = props.item.quantity"
                                      :rules="[max25chars]"
                                      label="Edit"
                                      single-line
                                      type="number"
                                      min=0 oninput="validity.valid||(value='');"
                                      dense
                                  ></v-text-field>
                                </v-col>
                              </template>
                              <template v-slot:item.total="{ item }">{{
                                  (item.total = 
                                      item.amount * item.quantity
                                  )
                                  }}
                              </template>
                           </v-data-table>
                           <template>
                              <v-row justify="end" no-gutters class="ma-0 pa-0" height="5px">
                                <v-col cols="12"
                                  sm="9"
                                  class="text-right">
                                  Cash On Hand:
                                </v-col>
                                <v-col cols="12"
                                  sm="3"
                                  class="text-right">
                                  {{formtCurrency(totalAmount)}}
                                </v-col>
                                  <v-col cols="12"
                                  sm="9"
                                  class="text-right">
                                  Prev. Cash Withdrawn:
                                </v-col>
                                <v-col cols="12"
                                  sm="3"
                                  class="text-right">
                                {{this.total_cash_withdrawn}}
                                </v-col>
                                <v-col cols="12"
                                  sm="9"
                                  class="text-right">
                                  Total Cash:
                                </v-col>
                                <v-col cols="12"
                                  sm="3"
                                  class="text-right">
                                  {{formtCurrency(totalAmount + total_cash_withdrawn)}}
                                </v-col>
                              </v-row>
                            </template>
                        </div>
                    </template>
                </div>
            </div>
          </template>
        </v-card-text>
        <v-card-text>
           <template>
             <v-row>
                <v-col cols="6">
                  <img src="/assets/rapidposcustom/images/MarcellinAggregateLogo.png" style="height:70%; width:80%;">
                </v-col>
                <v-col cols="6">
                  <v-data-table
                    :headers="showHeaders"
                    :items="dialog_data.payment_reconciliation"
                    item-key="mode_of_payment"
                    class="elevation-1"
                    :items-per-page="itemsPerPage"
                    hide-default-footer
                  >
                      <template v-slot:item.closing_amount="props">
                          <template v-if="props.item.mode_of_payment === 'Cash'">{{
                              (
                                props.item.closing_amount = (totalAmount)
                              )
                            }}
                          </template>
                          <template v-if="props.item.mode_of_payment === 'Credit Card'">
                            {{ total_credit_amount}}
                          </template>
                          <template v-if="props.item.mode_of_payment === 'Debit Card'">
                            {{ total_debit_amount}}
                          </template>
                      </template>

                      <template v-slot:item.opening_amount="{ item }">{{
                        formtCurrency(item.opening_amount)
                      }}</template>
                      <template v-slot:item.expected_amount="{ item }">{{
                        formtCurrency(item.expected_amount)
                      }}</template>
                      <template v-slot:item.difference="{ item }">{{
                        formtCurrency(item.difference = item.expected_amount - item.closing_amount)
                      }}</template>

                      <template slot="body.append">
                        <tr class="pink--text">
                            <th class="title">Totals</th>
                            <th class="title" text-aligh="center">{{totalAmount + total_credit_amount +  total_debit_amount}}</th>
                        </tr>
                      </template>
                  </v-data-table>
                </v-col>
             </v-row>
        </template>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="error" dark @click="close_dialog">Close</v-btn>
        <v-btn color="primary" dark @click="verify_submit">Submit</v-btn>
      </v-card-actions>

      </v-card>

    </v-dialog>

  </v-row>

</template>

<script>
import { evntBus } from '../../bus';

export default {
  data: () => ({
    activetab: '1',
    el: '#tabs',
    closingShiftDialog: false,
    verify_user: false,
    itemsPerPage: 13,
    show: false,
    pos_closing_shift: "",
    pos_closing_shift_data: {},
    cash_details: "",
    dialog_data: {},
    user: frappe.session.user,
    pos_close: '',
    pos_profile: "",
    pos_opening_shift: "",
    shift_number: "",
    inputUsername: null,
    inputPassword: null,
    denominations: [],
    cash_details_push: [],
    max25chars: (v) => v.length <= 20 || 'Input too long!', // TODO : should validate as number
    pagination: {},
    sample_items: [],
    checkout_counter:'',
    total_cash_withdrawn:0,
    total_debit_amount:0,
    total_credit_amount:0,
    num_invoices:0,
    headers: [
      {
        text: 'Opening Amount',
        align: 'end',
        sortable: true,
        value: 'opening_amount',
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
    headersMap: {
      mode_of_payment: {text: 'Mode of Payment', value: 'mode_of_payment'},
      closing_amount: {text: 'Closing Amount', value: 'closing_amount', align: 'center'}
    },
    selectedHeaders: [],
    
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
  }),
  watch: {},
  methods: {
    changeTab(tabIndexValue) {
      this.active_tab = tabIndexValue;
    },
    close_dialog() {
      this.closingShiftDialog = false;
    },
    close_verify_user() {
      this.verify_user = false;
    },

    view_opening_shift_details() {
      const vm = this;
      vm.sample_items.splice(0);
      frappe.call({
        method: 'posawesome.posawesome.api.custom_posapp.view_opening_shift_details',
        args: {
          opening_shift_name: this.dialog_data.pos_opening_shift
        },
        async: true,
        callback: function (r) {
          if(r.message){
            r.message.forEach((element) => {
              vm.sample_items.push(element)
            })
          }
        },
      });
    },
    view_cash_withdrawn(){
      const vm = this;
        frappe.call({
          method: 'posawesome.posawesome.api.custom_posapp.calculate_cash_withdrawn',
          args: {
            opening_shift_name: this.dialog_data.pos_opening_shift
          },
          async: true,
          callback: function (r) {
              if (r.message) {
                vm.total_cash_withdrawn = r.message.total_cash_withdrawn;
                vm.total_debit_amount = r.message.total_debit;
                vm.total_credit_amount = r.message.total_credit;
              }
        },
        });
    },
    // GET_DENOMINATIONS METHOD: List all cash denominations
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
    validateCashAndCounterDetails(){
    // Verify if denom is not empty
      this.denominations.forEach((element) => {
        if(element.quantity!=0){
         this.cash_details_push.push(element);
        }
      })
    //assign value to z-counter
      this.sample_items.forEach((element) => {
        if (element.name === "Z-Counter"){
            this.checkout_counter = element.value;
        }
      })
    },
    configure_modal() {
      if (!this.inputUsername || !this.inputPassword) {
        evntBus.$emit("show_mesage", {
          text: `Please complete the required fields`,
          color: "warning",
        })
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
                vm.view_opening_shift_details();
                vm.closingShiftDialog = true;
                vm.verify_user = false; 
                vm.inputUsername = null;
                vm.inputPassword = null;
                vm.shift_number = vm.pos_opening_shift.name;
                vm.num_invoices = vm.pos_opening_shift.no_of_invoices;
              }
            }
          })
      }
    },

    //CHECK NO OF INVOICES
    verify_submit() {
      if (this.num_invoices === 0) {
        evntBus.$emit("show_mesage", {
          text: `No transactions made`,
          color: "warning",
        });
      } else {
        this.submit_dialog();
      }
    },

    // SUBMIT_DIALOG METHOD: Submit POS Closing Shift data
    submit_dialog() {
      this.validateCashAndCounterDetails();
      this.pos_closing_shift_data.cash_details = this.cash_details_push;
      const pos_closing_shift_temp = this.pos_closing_shift_data;
      console.log({pos_closing_shift_temp});
      frappe
        .call("posawesome.posawesome.doctype.pos_closing_shift.custom_pos_closing_shift.submit_closing_shift", {
          closing_shift: this.dialog_data,
          closing_cash: this.pos_closing_shift_data,
          checkout_counter: this.checkout_counter
        })
        .then((r) => {
          if (r.message) {
            this.pos_closing_shift = r.message;
            this.load_print_page();
            evntBus.$emit("show_mesage", {
              text: `POS Shift Closed`,
              color: "success",
            });
            this.close_dialog();
            evntBus.$emit("check_opening_entry");
          } else {
            console.log(r)
          }
        });
    },
    load_print_page() {
      const url =
        frappe.urllib.get_base_url() +
        '/printview?doctype=POS%20Closing%20Shift&name=' +
        this.pos_closing_shift +
        '&trigger_print=1' +
        '&format=' +
        "Z Reading 2" +
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
    formtCurrency(value) {
      value = parseFloat(value);
      return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    },
    
    OpenClosingShift(e) {
      if (e.key === 'e' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
          this.verify_user = true;
        // this.closingShiftDialog = true;
      }
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
            evntBus.$emit("current_opening_shift", r.message);
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
  },

  created: function () {
    evntBus.$on('open_ClosingDialog2', (data) => {
      this.verify_user = true;
      this.dialog_data = data;
      this.view_cash_withdrawn();
    });
    document.addEventListener('keydown', this.OpenClosingShift.bind(this));

    this.$nextTick(function (){
      // this.check_opening_entry();
      this.get_denominations();
      evntBus.$on("submit_closing_pos", (data) => {
        this.submit_closing_pos(data)
      })
    });

    this.headers = Object.values(this.headersMap);
    this.selectedHeaders = this.headers;
  },
  
  destroyed() {
      document.removeEventListener('keydown', this.OpenClosingShift);
  },
  computed: {
    totalAmount: function(){

      return this.denominations.reduce(function(totalSum, item){

        return totalSum + (item.amount * item.quantity);
      },0);
    },
    showHeaders () {
      return this.headers.filter(s => this.selectedHeaders.includes(s));
    }
  }
};
</script>




<style lang="scss">

/*-------------------------STYLE CONFIGURATION---------------------*/

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
    padding: 30px 90px 10px 90px;
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
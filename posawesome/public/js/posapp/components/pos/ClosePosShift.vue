<!-- test -->
<template>
  <v-row justify="center">
      <!-- Verify username & password -->
    <v-dialog v-model="verify_user" max-width="500px">
      <v-card>
        <!-- Title -->
        <v-card-title>
          <span>POS Closing Shift</span>
          <v-spacer></v-spacer>
        </v-card-title>

        <!-- Username -->
        <v-row justify="center">
          <h4 style="color: rgb(155, 0, 0); --darkreader-inline-color:#ff6060;" data-darkreader-inline-color="">* Head Cashier or Sales manager only   </h4>
          <v-col
            cols="12"
            sm="7"
          >
          <v-text-field
              label="Username"
              v-model="inputUsername"
              clearable
              required
            ></v-text-field>
          </v-col>  
        </v-row>

        <!-- Password -->
        <v-row justify="center">
          <v-col
            cols="12"
            sm="7"
          >
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
          <v-btn color="error" dark @click="close_verify_dialog">Cancel</v-btn>
          <v-btn color="primary" @click="configure_modal">Verify</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Close POS Shift -->
    <!-- <v-dialog v-model="closingDialog" max-width="900px"> -->
    <v-dialog v-model="closingShiftDialog" max-width="900px">
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">Closing POS Shift v2</span>
        </v-card-title>
        <v-card-text>
          <template>
            <div class="tabs">
                <a v-on:click="activetab='1'" v-bind:class="[ activetab === '1' ? 'active' : '' ]">Tab 1</a>
                <a v-on:click="activetab='2'" v-bind:class="[ activetab === '2' ? 'active' : '' ]">Cash Breakdown</a>
            </div>
            <div class="content">
              <div v-if="activetab ==='1'" class="tabcontent">
                  <p>Todo...Tab 1</p>
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
                        <v-col
                          sm="7"
                        >
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
                      <template v-slot:item.total="{ item }">
                        {{
                          (item.total = 
                            item.amount * item.quantity
                          )
                        }}
                      </template>
                    </v-data-table>
                      <template>
                        <v-row justify="end" no-gutters class="ma-0 pa-0" height="5px">
                          <v-col
                            cols="12"
                            sm="9"
                            class="text-right">
                            Cash On Hand:
                          </v-col>
                          <v-col
                            cols="12"
                            sm="3"
                            class="text-right">
                            {{totalAmount}}
                          </v-col>
                            <v-col
                            cols="12"
                            sm="9"
                            class="text-right">
                            Prev. Cash Withdrawn:
                          </v-col>
                            <v-col
                              cols="12"
                              sm="3"
                              class="text-right">
                              1200
                            </v-col>
                          <v-col
                            cols="12"
                            sm="9"
                            class="text-right">
                            Total Cash:
                          </v-col>
                          <v-col
                            cols="12"
                            sm="3"
                            class="text-right">
                          {{totalAmount+1200}}
                          </v-col>
                        </v-row>
                      </template>
                  </div>
                </template>
              </div>
            </div>
          </template>
        </v-card-text>

        <template>
          <v-data-table
            :headers="headers"
            :items="dialog_data.payment_reconciliation"
            item-key="mode_of_payment"
            class="elevation-1"
            :items-per-page="itemsPerPage"
            hide-default-footer
          >
            <template v-slot:item.closing_amount="props">
              <v-edit-dialog
                :return-value.sync="props.item.closing_amount"
              >
                {{ formtCurrency(props.item.closing_amount) }}
                <template v-slot:input>
                  <v-text-field
                    v-model="props.item.closing_amount"
                    :rules="[max25chars]"
                    label="Edit"
                    single-line
                    counter
                    type="number"
                  ></v-text-field>
                </template>
              </v-edit-dialog>
            </template>
            <template v-slot:item.difference="{ item }">{{
              (item.difference = formtCurrency(
                item.expected_amount - item.closing_amount
              ))
            }}</template>
            <template v-slot:item.opening_amount="{ item }">{{
              formtCurrency(item.opening_amount)
            }}</template>
            <template v-slot:item.expected_amount="{ item }">{{
              formtCurrency(item.expected_amount)
            }}</template>
          </v-data-table>
        </template>

        <!-- <v-card-text class="pa-0">
          <v-container>
            <v-row>
              <v-col cols="12" class="pa-1">
                <template>
                  <v-data-table
                    :headers="headers"
                    :items="dialog_data.payment_reconciliation"
                    item-key="mode_of_payment"
                    class="elevation-1"
                    :items-per-page="itemsPerPage"
                    hide-default-footer
                  >
                    <template v-slot:item.closing_amount="props">
                      <v-edit-dialog
                        :return-value.sync="props.item.closing_amount"
                      >
                        {{ formtCurrency(props.item.closing_amount) }}
                        <template v-slot:input>
                          <v-text-field
                            v-model="props.item.closing_amount"
                            :rules="[max25chars]"
                            label="Edit"
                            single-line
                            counter
                            type="number"
                          ></v-text-field>
                        </template>
                      </v-edit-dialog>
                    </template>
                    <template v-slot:item.difference="{ item }">{{
                      (item.difference = formtCurrency(
                        item.expected_amount - item.closing_amount
                      ))
                    }}</template>
                    <template v-slot:item.opening_amount="{ item }">{{
                      formtCurrency(item.opening_amount)
                    }}</template>
                    <template v-slot:item.expected_amount="{ item }">{{
                      formtCurrency(item.expected_amount)
                    }}</template>
                  </v-data-table>
                </template>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text> -->
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">Close</v-btn>
          <!-- <v-btn color="primary" dark @click="submit_dialog">Submit</v-btn> -->
          <v-btn color="primary" dark @click="close_dialog">Submit</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from '../../bus';
export default {
  data: () => ({
    itemsPerPage: 20,
    dialog_data: {},
    verify_user: false,
    inputUsername: null,
    inputPassword: null,
    closingShiftDialog: false,
    show: false,
    activetab: '1',
    el: '#tabs',
    pos_closing_shift_data: {},
    cash_details: "",

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
    denominations: [],

    max25chars: (v) => v.length <= 20 || 'Input too long!', // TODO : should validate as number
    pagination: {},
  }),
  watch: {},
  methods: {
    // CHANGE TAB METHOD
    changeTab(tabIndexValue) {
      this.active_tab = tabIndexValue;
    },
    // CALCULATE TOTALS METHOD
    calculate_totals() {
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.custom_posapp.submit_total_closing_readings',
        args: {
          opening_shift:this.pos_closing_shift.name
        },
        async: true,
        callback: function (r) {
          //do nothing
        },
      });
    },
    close_dialog() {
        this.closingShiftDialog = false;
    },
    close_verify_dialog() {
        this.verify_user = false;
    },
    // submit_dialog() {
    //   evntBus.$emit('submit_closing_pos', this.dialog_data);
    //   this.closingDialog = false;
    // },

     // SUBMIT_DIALOG METHOD: Submit POS Closing Shift data
    submit_dialog() {
      this.cashDetailsMethod();
      this.pos_closing_shift_data.cash_details = this.cash_details_push;
      const pos_closing_shift_temp = this.pos_closing_shift_data;
      console.log({pos_closing_shift_temp});
      frappe
        .call("posawesome.posawesome.doctype.pos_closing_shift.custom_pos_closing_shift.submit_closing_shift", {
          closing_shift: this.dialog_data,
          closing_cash: this.pos_closing_shift_data,
        })
        .then((r) => {
          if (r.message) {
            this.pos_closing_shift = r.message.pos_closing_shift;
            // this.load_print_page();
            // evntBus.$emit("current_closing_shift", r.message);
            evntBus.$emit("show_mesage", {
              text: message,
              color: "success",
            });
            this.check_opening_entry()
          } else {
            console.log(r)
          }
        });
    },
    configure_modal() {
      if (!this.inputUsername || !this.inputPassword) {
        evntBus.$emit("show_mesage", {
          text: `Please complete the required fields`,
          color: "warning",
        })
      } else {
        // if (this.inputUsername === this.user && this.inputPassword) {
        //   frappe.call({
        //     method: "posawesome.posawesome.api.custom_posapp.verify_user",
        //     args: {
        //       username: this.inputUsername,
        //       password: this.inputPassword
        //     },
        //     callback: function(r) {
        //       if(!r.exc) {
        //         callback();
        //       }
        //     }
        //   })

          this.closingShiftDialog = true;
          this.verify_user = false;
          this.calculate_totals();
          this.inputUsername = null;
          this.inputPassword = null;
        //  } else {
        //   evntBus.$emit("show_mesage", {
        //     text: `Username does not match. Please try again.`,
        //     color: "error",
        //   })
        // }
      }
    },

    // GET_DENOMINATIONS METHOD: List all cash denominations
    get_denominations() {
      const vm = this;
        frappe.call({
          method: "posawesome.posawesome.api.custom_posapp.get_cash_denominations_breakdown",
           callback: function (r) {
          if (r.message) {
            r.message.get_denom.forEach((element) => {
              vm.denominations.push(element)
            })
          }
        },
        });
    },
    // CASH_DETAILS METHOD
    cashDetailsMethod(){
      this.denominations.forEach((element) => {
        if(element.quantity!=0){
         this.cash_details_push.push(element);
        }
      })
    },
    formtCurrency(value) {
      value = parseFloat(value);
      return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    },

    // CLOSING SHIFT SHORTCUT KEY METHOD
    OpenClosingShift(e) {
      if (e.key === 'e' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
          this.verify_user = true;
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
    });

    document.addEventListener('keydown', this.OpenClosingShift.bind(this));

    this.$nextTick(function (){
      this.get_denominations();
    });
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
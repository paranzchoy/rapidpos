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
              @keyup.enter="submit_dialog"
            ></v-text-field>
          </v-col>
        </v-row>

        <v-card-actions>
          <v-spacer></v-spacer>

          <!-- <v-btn color="error" dark @click="close_verify_dialog">Cancel</v-btn> -->

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
                           </v-data-table>
                        </div>
                    </template>
                </div>
            </div>
          </template>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">Close</v-btn>
          <v-btn color="primary" dark @click="submit_dialog">Submit</v-btn>
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
    inputUsername: null,
    inputPassword: null,
    denominations: [],
    cash_details_push: [],
    max25chars: (v) => v.length <= 20 || 'Input too long!', // TODO : should validate as number
    pagination: {},
    sample_items: []
  }),
  watch: {},
  methods: {
    changeTab(tabIndexValue) {
      this.active_tab = tabIndexValue;
    },
    close_dialog() {
      this.closingShiftDialog = false;
    },
    // close_verify_dialog() {
    //   this.verify_user = false;
    // },

    close_verify_user() {
      this.verify_user = false;
    },

    calculate_totals() {
      const vm = this;
      vm.sample_items.splice(0);
      frappe.call({
        method: 'posawesome.posawesome.api.custom_posapp.view_opening_shift_details',
        args: {
          opening_shift_name:"POSA-OS-21-0000016"
        },
        async: true,
        callback: function (r) {
          if(r.message){
            r.message.forEach((element) => {
              vm.sample_items.push(element)
              // console.log(element);
            })
          }
        },
      });
    },
    // GET_DENOMINATIONS METHOD: List all cash denominations
    get_denominations() {
      const vm = this;
        frappe.call({
          method: "rapidposcustom.rapidposcustom.api.rapidposcustom.get_cash_denominations_breakdown",
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
    configure_modal() {
      if (!this.inputUsername || !this.inputPassword) {
        evntBus.$emit("show_mesage", {
          text: `Please complete the required fields`,
          color: "warning",
        })
      } else {
        if (this.inputUsername === this.user && this.inputPassword) {
          this.calculate_totals();
          frappe.call({
            method: "posawesome.posawesome.api.custom_posapp.verify_user",
            args: {
              username: this.inputUsername,
              password: this.inputPassword
            },
            callback: function(r) {
              if(!r.exc) {
                callback();
              }
            }
          })
          this.closingShiftDialog = true;
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
    },

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
            evntBus.$emit("current_closing_shift", r.message);
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
    // evntBus.$on('current_closing_shift', (data) => {
    //   this.pos_closing_shift = data.pos_closing_shift;
    // });
    evntBus.$on('open_ClosingDialog2', (data) => {
      this.verify_user = true;
      this.dialog_data = data;
    });
    document.addEventListener('keydown', this.OpenClosingShift.bind(this));

    this.$nextTick(function (){
      this.get_denominations();

      evntBus.$on("submit_closing_pos", (data) => {
        this.submit_closing_pos(data)
      })
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
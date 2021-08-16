<template>
  <v-row justify="center">
    <v-dialog v-model="coupon_state" max-width="700px" min-width="700px">
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">Apply Coupon Code(s)</span>
        </v-card-title>
        <v-container>
          <v-row class="mb-4">
            <v-text-field
              color="indigo"
              label="Enter Coupon Code"
              background-color="white"
              hide-details
              dense
              clearable
              class="mx-4"
              v-model="coupon_code"
              @keyup.enter="add_coupon_code"
            ></v-text-field>
            <v-btn
              text
              class="ml-2"
              color="primary"
              dark
              @click="add_coupon_code"
              >Add</v-btn>
          </v-row>
          <v-row>
            <v-col cols="12" class="pa-1">
              <template>
              <v-data-table
                :headers = "headers"
                :items = "coupon_list"
                item-key = "coupon_code"
                class="elevation-1"
              >
                  <template v-slot:item.qty="props">
                    <v-edit-dialog
                      :return-value.sync="props.item.qty"
                    >
                      {{ props.item.qty }}
                      <template v-slot:input>
                        <v-text-field
                          v-model="props.item.qty"
                          label="#"
                          single-line
                          counter
                          type="number"
                        ></v-text-field>
                      </template>
                    </v-edit-dialog>
                  </template>
              </v-data-table>
              </template>
            </v-col>
          </v-row>
        </v-container>
        <v-card-actions class="mt-4">
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">Close</v-btn>
          <v-btn
            color="primary"
            dark
            @click="submit_dialog"
            >Apply</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from "../../bus";
export default {
  data: () => ({
      invoice_doc:'',
      coupon_state: false,
      dialog_data: false,
      coupon_code: '',
      coupon_details:'',
      coupon_list: [],
      headers: [
      {
        text: 'Coupon Code',
        align: 'start',
        sortable: false,
        value: 'coupon_code',
      },
      {
        text: 'Qty',
        sortable: false,
        value: 'qty',
      }
    ],
    selected:[],
    coupon_list_invoice:[]
  }),
  watch: {

  },
  methods: { 
      close_dialog(){
          this.coupon_state = false;
      },
      add_coupon_code(){
        const vm = this;
        if (vm.coupon_code){
          frappe.call({
            method: 'posawesome.posawesome.api.custom_posapp.submit_coupon_code',
            args: {
              coupon_code: vm.coupon_code
            },
            async: true,
            callback: function (r) {
              if (r.message) {
                if (r.message.error_message){
                    evntBus.$emit("show_mesage", {
                      text: r.message.error_message,
                      color: "error",
                    });
                }
                else{
                  //check if item exists, push to list if not and increment quantity if true
                    var exists = vm.coupon_list.some(function(field) {
                      return field.coupon_code === r.message.coupon_code
                    });
                    if (!exists){
                      vm.coupon_list.push({"coupon_code":r.message.coupon_code,"qty":1});
                    }
                    else{
                      vm.coupon_list.forEach(element => {
                        if(element.coupon_code === r.message.coupon_code){
                          element.qty++;
                        }
                      });
                    }
                    evntBus.$emit("show_mesage", {
                      text: "Coupon '" + r.message.coupon_code +"' added!",
                      color: "success",
                    });
                }
               
              }
            },
          });
        }
        else{
          evntBus.$emit("show_mesage", {
              text: `Enter coupon code!`,
              color: "error",
            });
        }
    
      },
      submit_dialog(){
        const vm = this;
        console.log(vm.coupon_list);
        frappe.call({
            method: 'posawesome.posawesome.api.custom_posapp.apply_coupons',
            args: {
              coupon_list: vm.coupon_list,
              invoice_doc: vm.invoice_doc
            },
            async: true,
            callback: function (r) {
              if (r.message) {
                if (r.message.error_messages.length != 0){
                   evntBus.$emit("show_mesage", {
                        text: r.message.error_messages[0],
                        color: "error",
                    });
                }
                else{
                    r.message.discount.forEach((element) => {
                      vm.coupon_list_invoice.push(element)
                    })
                    evntBus.$emit("submit_coupon", {
                        discount: vm.coupon_list_invoice
                    });
                    
                    vm.coupon_state = false;
                    vm.coupon_code = null;
                    vm.coupon_list.splice(0);
                }
              }
            },
          });
      }
  },
  created: function () {
    evntBus.$on('apply_coupon_code', (data) => {
        this.invoice_doc = data;
        this.coupon_state = true;
    });
  },
  computed: {

  }
};
</script>

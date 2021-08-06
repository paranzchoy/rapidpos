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
              @keyup.enter="submit_coupon_code"
            ></v-text-field>
            <v-btn
              text
              class="ml-2"
              color="primary"
              dark
              @click="submit_coupon_code"
              >Add</v-btn>
          </v-row>
          <v-row>
            <v-col cols="12" class="pa-1" v-if="dialog_data">
              <template>
                <v-data-table
                  :headers="headers"
                  :items="coupon_list"
                  item-key="name"
                  class="elevation-1"
                  hide-default-footer 
                  disable-pagination
                  dense
                  v-model="coupon_list"
                >
                  <!-- <template v-slot:item.grand_total="{ item }">{{
                    formtCurrency(item.grand_total)
                  }}</template> -->
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
      coupon_list: [],
      headers: [{text:'Coupon Name', value:'coupon_name'}, {text:'Qty', value:'qty'}],
    selected:''
  }),
  watch: {

  },
  methods: { 
      close_dialog(){
          this.coupon_state = false;
      },
      submit_coupon_code(){
        const vm = this;
        if (vm.coupon_code){
          frappe.call({
            method: 'posawesome.posawesome.api.custom_posapp.submit_coupon_code',
            args: {
              coupon_code: vm.coupon_code,
              invoice_name: this.invoice_doc.name
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
                  // vm.coupon_list.push({"coupon_name":r.message.coupon_code, "qty":0});
                  // console.log(vm.coupon_list);
                    evntBus.$emit("show_mesage", {
                      text: "Coupon '" + r.message.coupon_code +"' added!",
                      color: "success",
                    });
                    // vm.invoice_doc = r.message.invoice_doc;
                    // vm.invoice_doc.coupon_list.forEach((element) => {
                    // vm.coupon_list.push(element);
                  // })
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
    
      }
  },
  created: function () {
    evntBus.$on('apply_coupon_code', (data) => {
      this.invoice_doc = data;
      this.coupon_state = true;
      console.log(data);
    });
  },
  computed: {

  }
};
</script>

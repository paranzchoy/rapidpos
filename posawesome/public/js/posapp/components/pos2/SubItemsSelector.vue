<template>
  <v-row justify="center">
    <v-dialog v-model="dialog_state" max-width="1000px" scrollable>
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">Select subitems for {{item_doc.item_name}}</span>
        </v-card-title>
        <v-container>
          <v-row>
             <v-col cols="4">
                <v-combobox
                  v-model="item_group"
                  :items="subitem_item_group"
                  label="Item Group"
                  outlined
                  dense
                ></v-combobox>
            </v-col>
            <v-spacer></v-spacer>
            <v-col cols="3">
              Max. Qty left: {{remaining_qty}}
            </v-col>
          </v-row>
        </v-container>
        <v-divider></v-divider>
        <v-card-text>
          <v-row>
               <v-col
                v-for="(item) in filtred_items"
                :key="item.name"
                xl="2"
                lg="3"
                md="12"
                sm="12"
                cols="4"
                min-height="50"
              >
                <v-card hover="hover" @click="add_item(item)">
                      <v-col cols="12">
                        <v-img
                          :src="
                            item.image ||
                            '/assets/posawesome/js/posapp/components/pos/placeholder-image.png'
                          "
                          class="white--text align-end"
                          gradient="to bottom, rgba(0,0,0,.2), rgba(0,0,0,.7)"
                          height="100px"
                        >
                          <v-card-text
                            v-text="item.item_name"
                            class="text-subtitle-2 px-1 pb-2"
                          ></v-card-text>
                        </v-img>
                      </v-col>
                     <div class="text-caption indigo--text accent-3">
                        {{ item.rate || 0 }} {{ item.currency || '' }}
                     </div>
                </v-card>
                <v-col cols="12">
                        <v-card-text class="text--primary pa-1">
                            <v-text-field
                              v-model="item.actual_qty"
                              label="Qty"
                              type="number">
                            </v-text-field>
                        </v-card-text>
                </v-col>

              </v-col>
          </v-row>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="mt-4">
          <v-spacer></v-spacer>
          <v-btn color="blue-grey" dark @click="reset">Reset</v-btn>
          <v-btn color="error" dark @click="close_dialog">Cancel</v-btn>
          <v-btn
            color="primary"
            dark
            @click="submit_dialog"
            >Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>
<script>
import { evntBus } from "../../bus";
export default {
  data: () => ({
      pos_profile:'',
      invoice_doc:'',
      item_doc:'',
      dialog_state: false,
      hakdog:'',
      select: '',
      total_inputted_qty:0,
      items:[],
      item_group:'ALL',
      subitem_item_group:['ALL'],
      items_headers: [
      { text: 'Name', align: 'start', sortable: true, value: 'item_name' },
      { text: 'Rate', value: 'rate', align: 'start' },
      { text: 'Currency', value: 'currency', align: 'start' },
      { text: 'Available QTY', value: 'actual_qty', align: 'start' },
      { text: 'UOM', value: 'stock_uom', align: 'start' },
      ],
      itemsPerPage: 12,
  }),
  watch: {

  },
  methods: { 
      close_dialog(){
          this.dialog_state = false;
      },
      add_item(item){
        if (this.total_qty>=this.item_doc.max_subitem_quantity){
            evntBus.$emit('show_mesage', {
              text: `Quantity allowed exceeded!`,
              color: 'error',
            });
            frappe.utils.play_sound('error');
        }
        else{
            this.filtred_items.forEach((element) => {
              if (element===item){
                element.actual_qty++;
              }
            });
        }
      },
      submit_dialog(){
        let data = {};
        let selected_items = [];
        this.filtred_items.forEach((item) => {
            if (item.actual_qty){
              selected_items.push({'item_name': item.name, 'qty': item.actual_qty, 'rate': item.rate, 'uom': item.uom});
            }
        });
        data.item_doc = this.item_doc;
        data.selected_items = selected_items;
        evntBus.$emit('show_mesage', {
              text: `Subitems added!`,
              color: 'success',
        });
        frappe.utils.play_sound('submit');
        this.close_dialog();
        // const vm = this;
        // frappe.call({
        //   method: 'posawesome.posawesome.api.custom_posapp.submit_subitems',
        //   args: {
        //     data: data,
        //   },
        //   async: true,
        //   callback: function (r) {
        //     if (r.message) {
        //       vm.load_print_page();
        //       evntBus.$emit('show_mesage', {
        //         text: `Invoice ${r.message.name} is Submited`,
        //         color: 'success',
        //       });
        //       frappe.utils.play_sound('submit');
        //     }
        //   },
        // });
      },

      formtCurrency(value) {
        value = parseFloat(value);
        return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
      },
      get_items(){
          const vm = this;
          vm.items.splice(0);
          vm.pos_profile.subitem_trigger = true;
          frappe.call({
          method: 'posawesome.posawesome.api.custom_posapp.get_items',
          args: { pos_profile: vm.pos_profile },
          callback: function (r) {
            if (r.message) {
              vm.items = r.message;
              if (vm.pos_profile.posa_local_storage) {
                localStorage.setItem('items_storage', '');
                localStorage.setItem('items_storage', JSON.stringify(r.message));
                }
              }
            },
          });
      },
    get_search(first_search) {
      let search_term = '';
        if (first_search && first_search.startsWith(this.pos_profile.posa_scale_barcode_start)) {
          search_term = first_search.substr(0, 7);
        } 
        else {
          search_term = first_search;
        }
      return search_term;
    },
    reset(){
      this.filtred_items.forEach((element) => {
          element.actual_qty = '';
      });
    }
  },
  created: function () {
    evntBus.$on('open_items_selector', (data) => {
        this.item_doc = data.item;
        this.pos_profile = data.pos_profile;
        this.invoice_doc = data.invoice_doc;
        this.pos_profile.subitem_item_group.forEach(element => {
          if (element.item_group !== 'All Item Groups') {
            this.subitem_item_group.push(element.item_group);
          }
          this.select = this.subitem_item_group[0];
        });
        this.get_items();
        this.dialog_state = true;
    });
  },
  computed: {
    remaining_qty(){
      let diff_qty = (
        this.item_doc.max_subitem_quantity - this.total_qty
      )
      return diff_qty;
    },
    total_qty(){
        let total = 0;
          this.filtred_items.forEach((element) => {
              total += element.actual_qty;
          }
        )
        return total;
    },
     filtred_items() {
      this.search = this.get_search(this.first_search);
      let filtred_list = [];
      let filtred_group_list = [];
      if (this.item_group != 'ALL') {
        filtred_group_list = this.items.filter((item) =>
          item.item_group.toLowerCase().includes(this.item_group.toLowerCase())
        );
      } else {
        filtred_group_list = this.items;
      }
      if (!this.search || this.search.length < 3) {
        return (filtred_list = filtred_group_list.slice(0, 50));
      } else if (this.search) {
        filtred_list = filtred_group_list.filter((item) => {
          let found = false;
          for (let element of item.item_barcode) {
            if (element.barcode == this.search) {
              found = true;
              break;
            }
          }
          return found;
        });
        if (filtred_list.length == 0) {
          filtred_list = filtred_group_list.filter((item) =>
            item.item_name.toLowerCase().includes(this.search.toLowerCase())
          );
          if (filtred_list.length == 0) {
            filtred_list = filtred_group_list.filter((item) =>
              item.item_code.toLowerCase().includes(this.search.toLowerCase())
            );
          }
        }
      }
      return filtred_list.slice(0, 50);
    },

  }
};
</script>
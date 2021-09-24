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
      select: '',
      total_inputted_qty:0,
      items:[],
      item_groups:[],
      selected_item_groups:[],
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
          if (item.actual_qty!=0){
            selected_items.push({'item_name': item.item_name, 'qty': item.actual_qty, 'rate': item.rate*item.actual_qty, 'uom': item.stock_uom});
          }
      });
      data.item_name = this.item_doc.item_name;
      data.invoice_name = this.invoice_doc.name;
      data.selected_items = selected_items;
      this.send_subitems_to_invoice(data);
      this.save_subitems(data);
      this.close_dialog();
    },

    send_subitems_to_invoice(data){
        evntBus.$emit("save_subitems", this.filtred_items, data);
    },

    save_subitems(data){
        const vm = this;
        frappe.call({
          method: 'posawesome.posawesome.api.custom_posapp.save_subitems',
          args: {
            data: data
          },
          callback: function (r) {
            if (r.message) {
                vm.invoice_doc = r.message.invoice_doc;
                evntBus.$emit("submit_subitems", r.message);
                evntBus.$emit('show_mesage', {
                  text: `Subitems added!`,
                  color: 'success',
                });
                frappe.utils.play_sound('submit');
                
                
            }
          },
        });
    },
    formtCurrency(value) {
        value = parseFloat(value);
        return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    },
    get_item_groups(){
       const vm = this;
       frappe.call({
          method: 'posawesome.posawesome.api.custom_posapp.get_product_item_groups',
          args: { item_doc: vm.item_doc },
          callback: function (r) {
            if (r.message) {
              console.log(r.message);
              r.message.forEach(element => {
                if (element.item_group !== 'All Item Groups') {
                  vm.subitem_item_group.push(element.item_group);
                  vm.item_groups.push({"item_group":element.item_group});
                }
              });
              }
            vm.select = vm.subitem_item_group[0];
            },
          });

    },
    get_items(){
          this.items.splice(0);
          this.pos_profile.subitem_item_group = this.item_groups;
          this.pos_profile.subitem_trigger = true;

          const vm = this;
          frappe.call({
          method: 'posawesome.posawesome.api.custom_posapp.get_items',
          args: { pos_profile: vm.pos_profile },
          callback: function (r) {
            if (r.message) {
                vm.items = r.message;
              }
            },
          });
    },
    get_existing_subitems(subitems){
      this.filtred_items=subitems;
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
          element.actual_qty = 0;
      });
    },
    check_item_subitems(){
      if(this.item_doc.subitems){
        this.get_existing_subitems(this.item_doc.subitems);
      }
      else{
        this.get_items();
      }
    }
  },
  created: function () {
    evntBus.$on('open_items_selector', (data) => {
        this.item_doc = data.item;
        this.pos_profile = data.pos_profile;
        this.invoice_doc = data.invoice_doc;
        this.get_item_groups();
        this.check_item_subitems();
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
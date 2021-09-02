<template>
  <v-row justify="center">
    <v-dialog v-model="dialog_state" max-width="700px" scrollable>
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">Select subitems for {{item_doc.item_name}}</span>
        </v-card-title>
        <v-container>
          <v-row>
             <v-col cols="4">
                <v-combobox
                  v-model="select"
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
                v-for="(item) in items"
                :key="item.name"
                xl="2"
                lg="3"
                md="12"
                sm="12"
                cols="4"
                min-height="50"
              >
                <!-- <v-card hover="hover" @click="add_item(item)"> -->
                <v-card hover="hover">
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
                </v-card>
                <v-col cols="12">
                        <v-card-text class="text--primary pa-1">
                          <div class="text-caption indigo--text accent-3">
                            <!-- {{ item.rate || 0 }} {{ item.currency || '' }} -->
                            <v-text-field
                              v-model="item.total_qty"
                              label="Qty"
                              type="number"
                            ></v-text-field>
                          </div>
                        </v-card-text>
                </v-col>

              </v-col>
          </v-row>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="mt-4">
          <v-spacer></v-spacer>
          <v-btn color="blue-grey" dark @click="close_dialog">Reset</v-btn>
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
    filtred_items(data_value) {
      this.update_items_details(data_value);
    },
  },
  methods: { 
      close_dialog(){
          this.dialog_state = false;
      },
      
      submit_dialog(){
        
      },

      formtCurrency(value) {
        value = parseFloat(value);
        return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
      },
      get_items(){
          const vm = this;
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
      update_items_details(items) {
        const vm = this;
        frappe.call({
          method: 'posawesome.posawesome.api.posapp.get_items_details',
          args: {
            pos_profile: vm.pos_profile,
            items_data: items,
          },
          callback: function (r) {
            if (r.message) {
              items.forEach((item) => {
                const updated_item = r.message.find(
                  (element) => element.item_code == item.item_code
                );
                item.actual_qty = updated_item.actual_qty;
                item.serial_no_data = updated_item.serial_no_data;
                item.batch_no_data = updated_item.batch_no_data;
                item.item_uoms = updated_item.item_uoms;
              });
            }
          },
        });
      },
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
        this.item_doc.max_subitem_quantity - this.total_inputted_qty
      )
      return diff_qty;
    }

  }
};
</script>
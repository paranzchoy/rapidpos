<template>
  <v-row justify="center">
    <v-dialog v-model="dialog_state" max-width="700px" min-width="700px">
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">Select subitems for {{item_doc.item_name}}</span>
        </v-card-title>
        <v-container>
          <v-row class="mb-4">
             <v-col cols="4">
                <v-combobox
                  v-model="select"
                  :items="item_doc.item_group"
                  label="Item Group"
                  outlined
                  dense
                ></v-combobox>
            </v-col>
            <v-spacer></v-spacer>
            <v-col cols="3">
              Max. Qty left: 12
            </v-col>
          </v-row>
          <v-row>
          </v-row>
        </v-container>
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
      item_doc:'',
      dialog_state: false,
      select: ''
  }),
  watch: {

  },
  methods: { 
      close_dialog(){
          this.dialog_state = false;
      },
      
      submit_dialog(){
        
      }
  },
  created: function () {
    evntBus.$on('open_items_selector', (item) => {
        this.item_doc = item;
        this.dialog_state = true;
    });
  },
  computed: {

  }
};
</script>
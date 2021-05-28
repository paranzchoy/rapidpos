<template>
  <v-row justify="center">
    <v-dialog v-model="helpDialog" max-width="600">
      <!-- <template v-slot:activator="{ on, attrs }">
        <v-btn color="primary" dark v-bind="attrs" v-on="on">Open Dialog</v-btn>
      </template>-->
      <v-card>

      <v-card-title class="headline grey lighten-2">
      POS Help
      </v-card-title>

      <v-container class="grey lighten-5">

        <v-row no-gutters>
              <v-col cols="1" sm="3" md="2">
                  <v-card class="pa-2" outlinedtile>
                      <div class="font-weight-medium">F1</div>
                  </v-card>
              </v-col>
              <v-col cols="4" md="4">
                  <v-card class="pa-2" outlined tile>
                    Help
                  </v-card>
              </v-col>
              <v-col cols="3" sm="3" md="2">
                  <v-card class="pa-2" outlinedtile>
                      <div class="font-weight-medium">Ctrl + D</div>
                  </v-card>
              </v-col>
              <v-col cols="4" md="4" sm="3">
                  <v-card class="pa-2" outlined tile>
                    Delete First Item
                  </v-card>
              </v-col>
        </v-row>

      <v-row no-gutters>
            <v-col cols="2" sm="3" md="2">
                <v-card class="pa-2" outlinedtile>
                    <div class="font-weight-medium">F2</div>
                </v-card>
            </v-col>
            <v-col cols="4" md="4">
                <v-card class="pa-2" outlined tile>
                  Quantity
                </v-card>
            </v-col>
            <v-col cols="2" sm="3" md="2">
                <v-card class="pa-2" outlinedtile>
                    <div class="font-weight-medium">Ctrl + O</div>
                </v-card>
            </v-col>
            <v-col cols="4" md="4">
                <v-card class="pa-2" outlined tile>
                  Open First Item
                </v-card>
            </v-col>
      </v-row>

      <v-row no-gutters>
            <v-col cols="2" sm="3" md="2">
                <v-card class="pa-2" outlinedtile>
                    <div class="font-weight-medium">F3</div>
                </v-card>
            </v-col>
            <v-col cols="4" md="4">
                <v-card class="pa-2" outlined tile>
                  Item Selector
                </v-card>
            </v-col><v-col cols="2" sm="3" md="2">
                <v-card class="pa-2" outlinedtile>
                    <div class="font-weight-medium">Ctrl + R</div>
                </v-card>
            </v-col>
            <v-col cols="4" md="4">
                <v-card class="pa-2" outlined tile>
                  Reprint Invoice
                </v-card>
            </v-col>
      </v-row>

      <v-row no-gutters>
            <v-col cols="2" sm="3" md="2">
                <v-card class="pa-2" outlinedtile>
              <div class="font-weight-medium">F4</div>
              </v-card>
            </v-col>
            <v-col cols="4" md="4">
              <v-card class="pa-2" outlined tile>
                Customer Field
              </v-card>
            </v-col>
            <v-col cols="2" sm="3" md="2">
              <v-card class="pa-2" outlinedtile>
                  <div class="font-weight-medium">Ctrl + X</div>
              </v-card>
            </v-col>
            <v-col cols="4" md="4">
              <v-card class="pa-2" outlined tile>
                Print X-Reading Report
              </v-card>
            </v-col>
      </v-row>

      <v-row no-gutters>
          <v-col cols="2" sm="3" md="2">
            <v-card class="pa-2" outlinedtile>
                <div class="font-weight-medium">F5</div>
            </v-card>
          </v-col>
          <v-col cols="4" md="4">
            <v-card class="pa-2" outlined tile>
              Cash payment
            </v-card>
          </v-col>
          <v-col cols="2" sm="3" md="2">
            <v-card class="pa-2" outlinedtile>
                <div class="font-weight-medium">Ctrl + I</div>
            </v-card>
          </v-col>
          <v-col cols="4" md="4">
            <v-card class="pa-2" outlined tile>
              Idle
            </v-card>
          </v-col>
      </v-row>

      <v-row no-gutters>
          <v-col cols="2" sm="3" md="2">
            <v-card class="pa-2" outlinedtile>
                <div class="font-weight-medium">F6</div>
            </v-card>
          </v-col>
          <v-col cols="4" md="4">
            <v-card class="pa-2" outlined tile>
              Card Payment
            </v-card>
          </v-col>
          <v-col cols="2" sm="3" md="2">
            <v-card class="pa-2" outlinedtile>
                <div class="font-weight-medium">Ctrl + L</div>
            </v-card>
          </v-col>
          <v-col cols="4" md="4">
            <v-card class="pa-2" outlined tile>
              Cash Withdrawal
            </v-card>
          </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col cols="2" sm="3" md="2">
          <v-card class="pa-2" outlinedtile>
              <div class="font-weight-medium">F7</div>
          </v-card>
        </v-col>
        <v-col cols="4" md="4">
          <v-card class="pa-2" outlined tile>
            Enable Discount
          </v-card>
        </v-col>
        <v-col cols="2" sm="3" md="2">
          <v-card class="pa-2" outlinedtile>
              <div class="font-weight-medium">Ctrl + E</div>
          </v-card>
        </v-col>
        <v-col cols="4" md="4">
          <v-card class="pa-2" outlined tile>
            Close Shift
          </v-card>
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col cols="2" sm="3" md="2">
          <v-card class="pa-2" outlinedtile>
              <div class="font-weight-medium">F8</div>
          </v-card>
        </v-col>
        <v-col cols="4" md="4">
          <v-card class="pa-2" outlined tile>
            Get Hold
          </v-card>
        </v-col>
         <v-col cols="2" sm="3" md="2">
          <v-card class="pa-2" outlinedtile>
              <div class="font-weight-medium">Ctrl + 1</div>
          </v-card>
        </v-col>
        <v-col cols="4" md="4">
          <v-card class="pa-2" outlined tile>
            Cash Payment
          </v-card>
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col cols="2" sm="3" md="2">
          <v-card class="pa-2" outlinedtile>
              <div class="font-weight-medium">F9</div>
          </v-card>
        </v-col>
        <v-col cols="4" md="4">
          <v-card class="pa-2" outlined tile>
            Return
          </v-card>
        </v-col>
         <v-col cols="2" sm="3" md="2">
          <v-card class="pa-2" outlinedtile>
              <div class="font-weight-medium">Ctrl + 2</div>
          </v-card>
        </v-col>
        <v-col cols="4" md="4">
          <v-card class="pa-2" outlined tile>
            Credit Card Payment
          </v-card>
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col cols="2" sm="3" md="2">
          <v-card class="pa-2" outlinedtile>
              <div class="font-weight-medium">F10</div>
          </v-card>
        </v-col>
        <v-col cols="4" md="4">
          <v-card class="pa-2" outlined tile>
            Cancel Invoice
          </v-card>
        </v-col>
        <v-col cols="2" sm="3" md="2">
          <v-card class="pa-2" outlinedtile>
              <div class="font-weight-medium">Ctrl + 3</div>
          </v-card>
        </v-col>
        <v-col cols="4" md="4">
          <v-card class="pa-2" outlined tile>
            Debit Card Payment
          </v-card>
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col cols="2" sm="3" md="2">
          <v-card class="pa-2" outlinedtile>
              <div class="font-weight-medium">F11</div>
          </v-card>
        </v-col>
        <v-col cols="4" md="4">
          <v-card class="pa-2" outlined tile>
            New Invoice
          </v-card>
        </v-col>
        <v-col cols="2" sm="3" md="2">
          <v-card class="pa-2" outlinedtile>
              <div class="font-weight-medium">Ctrl + 4</div>
          </v-card>
        </v-col>
        <v-col cols="4" md="4">
          <v-card class="pa-2" outlined tile>
            Coupon Payment
          </v-card>
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col cols="2" sm="3" md="2">
          <v-card class="pa-2" outlinedtile>
              <div class="font-weight-medium">F12</div>
          </v-card>
        </v-col>
        <v-col cols="4" md="4">
          <v-card class="pa-2" outlined tile>
            New Customer
          </v-card>
        </v-col>
      </v-row>



    <!-- <v-row no-gutters>
      <v-col cols="4" sm="3" md="3">
        <v-card class="pa-2" outlinedtile>
        <div class="font-weight-medium">Ctrl + Z</div>
        </v-card>
      </v-col>
      <v-col cols="6" md="8">
        <v-card class="pa-2" outlined tile>
          Select % (Add. Discount)
        </v-card>
      </v-col>
    </v-row> -->
    <!-- <v-row no-gutters>
      <v-col cols="4" sm="3" md="3">
        <v-card class="pa-2" outlinedtile>
        <div class="font-weight-medium">Ctrl + X</div>
        </v-card>
      </v-col>
      <v-col cols="6" md="8">
        <v-card class="pa-2" outlined tile>
          Close Modal
        </v-card>
      </v-col>
    </v-row> -->
      <!-- <v-row no-gutters>
      <v-col cols="4" sm="3" md="3">
        <v-card class="pa-2" outlinedtile>
        <div class="font-weight-medium">F8</div>
        </v-card>
      </v-col>
      <v-col cols="6" md="8">
        <v-card class="pa-2" outlined tile>
          POS Help
        </v-card>
      </v-col>
    </v-row> -->
    </v-container>
         <v-card-actions>
          <v-spacer></v-spacer>
              <v-btn
                color="primary"
                text
                @click="close_dialog"
              >
                Close
              </v-btn>
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
    helpDialog: false,

              }),
  watch: {},
  methods: {
      close_dialog() {
      this.helpDialog = false;
      },
    },


  created: function () {
    evntBus.$on("open_help", () => {
      this.helpDialog = true;
    });
  },
};

</script>

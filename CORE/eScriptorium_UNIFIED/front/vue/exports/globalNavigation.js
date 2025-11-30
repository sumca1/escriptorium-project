import Vue from "vue";
import { registerMessages } from "./i18nInjector";

// Register i18n translations FIRST, before any components load
registerMessages();

import store from "../store";
import GlobalNavigation from "../components/GlobalNavigation/GlobalNavigation.vue";
import "../index.css";

export default new Vue({
    el: "#vue-global-nav",
    store,
    components: {
        "global-navigation": GlobalNavigation,
    },
});

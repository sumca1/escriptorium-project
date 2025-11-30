<template>
    <div>
        <h3>{{ translate('Import images from IIIF') }}</h3>
        Input a valid IIIF manifest URI to import all of its images in full resolution
        along with its metadata.
        <fieldset>
            <TextField :label="translate('IIIF Manifest URI')"
                :placeholder="translate('IIIF manifest URL')"
                :invalid="invalid['iiifUri']"
                :on-input="handleIIIFInput"
                :value="iiifUri"
                :max-length="255"
            />
        </fieldset>
    </div>
</template>
<script>
import { mapActions, mapState } from "vuex";
import TextField from "../TextField/TextField.vue";

export default {
    name: "EscrImportIIIFForm",
    components: { TextField },
    props: {
        invalid: {
            type: Object,
            required: true,
        },
    },
    computed: {
        ...mapState({
            iiifUri: (state) => state.forms.import.iiifUri,
        })
    },
    methods: {
        ...mapActions("forms", [
            "handleGenericInput",
        ]),
        handleIIIFInput(e) {
            this.handleGenericInput({
                form: "import",
                field: "iiifUri",
                value: e.target.value,
            });
        },
    },
}
</script>

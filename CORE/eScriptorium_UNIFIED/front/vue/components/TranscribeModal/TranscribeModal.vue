<template>
    <EscrModal
        class="escr-transcribe-modal"
    >
        <template #modal-header>
            <h2>{{ translate('transcribe') }} {{ scope }}</h2>
            <EscrButton
                color="text"
                :on-click="onCancel"
                size="small"
            >
                <template #button-icon>
                    <XIcon />
                </template>
            </EscrButton>
        </template>
        <template #modal-content>
            <EscrAlert
                color="secondary"
                message="Check accuracy of segmentation prior to transcribing."
            />
            <DropdownField
                :label="translate('Model')"
                :disabled="disabled || !models"
                :options="modelOptions"
                :on-change="handleModelChange"
                required
            />
            <TextField
                :disabled="disabled" :help-text="translate('Enter a name for the new transcription layer.')"
                :max-length="512"
                :on-input="handleLayerNameInput"
                :value="layerName"
                :placeholder="translate('Enter layer name')"
                :label="translate('Layer Name')"
                required
            />
        </template>
        <template #modal-actions>
            <EscrButton
                color="outline-primary"
                :label="translate('Cancel')"
                :on-click="onCancel"
                :disabled="disabled"
            />
            <EscrButton
                color="primary"
                :label="translate('Transcribe')"
                :on-click="onSubmit"
                :disabled="disabled || invalid"
            />
        </template>
    </EscrModal>
</template>
<script>
import { mapActions, mapState } from "vuex";
import DropdownField from "../Dropdown/DropdownField.vue";
import EscrAlert from "../Alert/Alert.vue";
import EscrButton from "../Button/Button.vue";
import EscrModal from "../Modal/Modal.vue";
import TextField from "../TextField/TextField.vue";
import XIcon from "../Icons/XIcon/XIcon.vue";
import "../Common/Form.css";

export default {
    name: "EscrTranscribeModal",
    components: {
        DropdownField,
        EscrAlert,
        EscrButton,
        EscrModal,
        TextField,
        XIcon,
    },
    props: {
        /**
         * Boolean indicating whether or not the form fields should be disabled.
         */
        disabled: {
            type: Boolean,
            required: true,
        },
        /**
         * The list of all OCR models on the document. Should be an array of objects
         * with at least a name and pk for each model.
         */
        models: {
            type: Array,
            required: true,
        },
        /**
         * Scope of the transcription task, which will appear in the header to indicate
         * whether you are transcribing the entire document or specific images.
         */
        scope: {
            type: String,
            required: true,
        },
        /**
         * Callback function for submitting the transcription task.
         */
        onSubmit: {
            type: Function,
            required: true,
        },
        /**
         * Callback function for clicking "cancel".
         */
        onCancel: {
            type: Function,
            required: true,
        },
    },
    computed: {
        ...mapState({
            model: (state) => state.forms.transcribe.model,
            layerName: (state) => state.forms.transcribe.layerName,
        }),
        /**
         * this form is invalid and cannot be submitted if it is missing model
         * or layer name
         */
        invalid() {
            return !this.layerName || !this.model;
        },
        /**
         * convert models to options for select element
         */
        modelOptions() {
            return this.models.map((model) => ({
                label: model.name,
                value: model.pk.toString(),
                selected: this.model.toString() === model.pk.toString(),
            }));
        },
    },
    methods: {
        ...mapActions("forms", [
            "handleGenericInput",
        ]),
        handleLayerNameInput(e) {
            this.handleGenericInput({
                form: "transcribe", field: "layerName", value: e.target.value,
            });
        },
        handleModelChange(e) {
            this.handleGenericInput({ form: "transcribe", field: "model", value: e.target.value });
        },
    },
};
</script>

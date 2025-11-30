<template>
    <div
        v-if="data.models && data.models.length"
        class="escr-models-panel"
    >
        <details
            v-for="model in data.models"
            :key="model.pk"
            class="escr-model-details"
        >
            <summary>
                <span>{{ model.name }}</span>
                <a
                    :href="model.file"
                    aria-label="הורד קובץ מודל"
                >
                    <DownloadIcon />
                </a>
            </summary>
            <dl>
                <dt>תפקיד</dt>
                <dd>{{ model.job }}</dd>
                <dt>כתב</dt>
                <dd>{{ model.script || "-" }}</dd>
                <dt>גודל</dt>
                <dd>{{ filesize(model.file_size) }}</dd>
                <dt>אומן מ</dt>
                <dd>{{ model.parent || "-" }}</dd>
                <dt>סטטוס אימון</dt>
                <dd><component :is="trainedStatusIcon(model.training)" /></dd>
                <dt>דיוק</dt>
                <dd>
                    {{ model.accuracy_percent ? `${model.accuracy_percent.toFixed(2)}%` : "-" }}
                </dd>
                <dt>זכויות</dt>
                <dd>{{ model.rights }}</dd>
                <dt>שיתוף</dt>
                <dd v-if="model.can_share">
                    <a :href="`/model/${model.pk}/rights/`">שתף</a>
                </dd>
                <dd v-else>
                    -
                </dd>
            </dl>
        </details>
    </div>
    <EscrLoader
        v-else
        :loading="data.loading"
        no-data-message="אין מודלים להצגה."
    />
</template>
<script>
import CheckIcon from "../Icons/CheckIcon/CheckIcon.vue";
import DownloadIcon from "../Icons/DownloadIcon/DownloadIcon.vue";
import EscrLoader from "../Loader/Loader.vue";
import XIcon from "../Icons/XIcon/XIcon.vue";
import { filesizeformat } from "../../store/util/filesize";
import "./ModelsPanel.css";

export default {
    name: "EscrModelsPanel",
    components: { DownloadIcon, EscrLoader },
    props: {
        data: {
            type: Object,
            required: true,
        },
    },
    methods: {
        /**
         * Get the correct "Trained" icon (Check or X) for training status.
         */
        trainedStatusIcon(training) {
            return training === true ? XIcon : CheckIcon;
        },
        /**
         * Format the filesize similarly to how Django formats it.
         */
        filesize(bytes) {
            return filesizeformat(bytes);
        },
    }
}
</script>

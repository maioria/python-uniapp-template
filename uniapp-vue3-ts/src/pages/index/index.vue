<template>
  <view>
    <CommonHeader>
      <template v-slot:content>
        <text>Index</text>
      </template>
    </CommonHeader>
    <view>
      Index
    </view>
  </view>
</template>

<script setup lang="ts">
import CommonHeader from "@/components/CommonHeader.vue";

import { onMounted } from "vue";

onMounted(() => {
  uni.setNavigationBarTitle({
    title: "Index",
  });
});

</script>

<template>
  <!-- 全屏地球容器 -->
  <div id="cesiumContainer">
    <div class="tools">
      <button
        @click="addCogImageryLayer('http://localhost:8089/tif/big_cog.tif')"
      >
        添加图层
      </button>
      <button
        @click="
          addCogImageryLayer(
            'http://localhost:10086/fs/D/nginx-1.24.0/html/tif/test_cog.tif',
          )
        "
      >
        添加图层2
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
// 直接引入 Cesium
import * as Cesium from 'cesium';
import { addCogImageryLayer } from './utils/ImageryLayer';

onMounted(() => {
  // 初始化地球
  window.viewer = new Cesium.Viewer('cesiumContainer', {
    // 基础配置，最简启动
    timeline: false, // 隐藏时间轴
    animation: false, // 隐藏动画控件
    baseLayerPicker: false, // 隐藏图层选择
  });

  // 去掉默认版权信息（可选）
});
</script>

<style scoped>
/* 让地球全屏 */
#cesiumContainer {
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.tools {
  position: absolute;
  top: 10px;
  left: 10px;
  background-color: rgba(255, 255, 255, 0.8);
  padding: 5px;
  border-radius: 5px;
  z-index: 1000;
}
</style>

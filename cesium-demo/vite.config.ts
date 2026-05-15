import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
// 引入 cesium 插件
import cesium from 'vite-plugin-cesium';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), cesium()], // 直接使用即可
});

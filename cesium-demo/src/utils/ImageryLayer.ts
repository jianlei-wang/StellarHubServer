import { useCogTif } from './CogTif';

let cogTools: any = null;

export async function addCogImageryLayer(url: string) {
  // 添加 COG 图片层
  if (!cogTools) {
    cogTools = useCogTif(() => window.viewer);
  }
  try {
    const currentCogId = 'cogLayer';
    const cogConfig = {
      colormap: 'viridis',
      stretch: 'linear',
    };
    const info = await cogTools.addCogLayer(currentCogId, url, {
      colormap: cogConfig.colormap,
      stretch: cogConfig.stretch,
      flyTo: true,
    });
    console.log('[COG] addCogImageryLayer', info);
  } catch (error) {}
}

/**
 * 获取图层
 * @param id 图层id
 */

export function getImageryLayer(id: string) {
  // @ts-ignore
  return window.viewer.imageryLayers._layers.find(
    (layer: any) => layer.id === id,
  );
}

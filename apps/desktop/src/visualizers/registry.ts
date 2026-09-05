import { CrystalVisualizer } from "./crystal/CrystalVisualizer";
import type { VisualizerDefinition } from "./types";

export const visualizers = {
  crystal: {
    id: "crystal",
    name: "Cristal",
    description: "Forma cristalina facetada y dinámica.",
    component: CrystalVisualizer,
  },
} satisfies Record<string, VisualizerDefinition>;

export type VisualizerId = keyof typeof visualizers;

export function getVisualizer(id: VisualizerId): VisualizerDefinition {
  return visualizers[id];
}
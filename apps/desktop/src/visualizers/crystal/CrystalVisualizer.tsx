import type { VisualizerProps } from "../types";
import { CrystalScene } from "./CrystalScene";

export function CrystalVisualizer({
  accentColor,
}: VisualizerProps) {
  return (
    <div className="crystal-visualizer">
      <CrystalScene accentColor={accentColor} />
    </div>
  );
}
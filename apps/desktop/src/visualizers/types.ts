import type { ComponentType } from "react";

export type CelesteState =
  | "idle"
  | "listening"
  | "thinking"
  | "speaking";

export interface VisualizerProps {
  state: CelesteState;
  audioLevel: number;
  accentColor: string;
}

export interface VisualizerDefinition {
  id: string;
  name: string;
  description: string;
  component: ComponentType<VisualizerProps>;
}
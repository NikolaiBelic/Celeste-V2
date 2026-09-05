import { Canvas } from "@react-three/fiber";

import { CrystalAura } from "./CrystalAura";
import { CrystalBody } from "./CrystalBody";
import { CrystalInnerCore } from "./CrystalInnerCore";
import { CrystalEnvironment } from "./lighting/CrystalEnvironment";
import { CrystalLighting } from "./lighting/CrystalLighting";

interface CrystalSceneProps {
  accentColor: string;
}

export function CrystalScene({
  accentColor,
}: CrystalSceneProps) {
  return (
    <Canvas
      camera={{
        position: [0, 0, 5],
        fov: 42,
      }}
      dpr={[1, 2]}
      gl={{
        antialias: true,
        alpha: true,
      }}
    >
      <CrystalEnvironment accentColor={accentColor} />

      <CrystalLighting accentColor={accentColor} />

      <CrystalAura accentColor={accentColor} />

      <group scale={0.48}>
        <CrystalInnerCore accentColor={accentColor} />
        <CrystalBody accentColor={accentColor} />
      </group>
    </Canvas>
  );
}
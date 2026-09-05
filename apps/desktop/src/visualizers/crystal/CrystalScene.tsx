import { Canvas } from "@react-three/fiber";
import { CrystalBody } from "./CrystalBody";
import { CrystalInnerCore } from "./CrystalInnerCore";
import { CrystalPostProcessing } from "./effects/CrystalPostProcessing";

interface CrystalSceneProps {
  accentColor: string;
}

export function CrystalScene({ accentColor }: CrystalSceneProps) {
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
      <ambientLight intensity={0.5} />

      <pointLight
        position={[3, 2, 4]}
        color={accentColor}
        intensity={45}
        distance={10}
        />

    <pointLight
    position={[-3, -2, 2]}
    color={accentColor}
    intensity={22}
    distance={8}
    />
      <CrystalInnerCore accentColor={accentColor} />
        <CrystalBody accentColor={accentColor} />

        <CrystalPostProcessing />
    </Canvas>
  );
}
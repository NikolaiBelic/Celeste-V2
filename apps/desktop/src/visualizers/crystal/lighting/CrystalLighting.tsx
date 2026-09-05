interface CrystalLightingProps {
  accentColor: string;
}

export function CrystalLighting({
  accentColor,
}: CrystalLightingProps) {
  return (
    <>
      {/*
       * Luz ambiente mínima.
       * Conserva los negros profundos del cristal.
       */}
      <ambientLight intensity={0.12} />

      {/*
       * Luz principal neutra.
       * Revela las facetas sin teñir toda la esfera de naranja.
       */}
      <directionalLight
        position={[4, 5, 5]}
        color="#d8e0e8"
        intensity={2.2}
      />

      {/*
       * Contraluz ligeramente fría.
       * Separa los bordes oscuros del fondo.
       */}
      <directionalLight
        position={[-4, 1, 3]}
        color="#8795a8"
        intensity={1.15}
      />

      {/*
       * Energía naranja principal.
       * Debe sentirse localizada, no como iluminación global.
       */}
      <pointLight
        position={[1.8, 0.8, 2.2]}
        color={accentColor}
        intensity={14}
        distance={6}
        decay={2}
      />

      {/*
       * Energía secundaria desde abajo/lateral.
       */}
      <pointLight
        position={[-1.6, -1.2, 1]}
        color={accentColor}
        intensity={6}
        distance={4.5}
        decay={2}
      />
    </>
  );
}
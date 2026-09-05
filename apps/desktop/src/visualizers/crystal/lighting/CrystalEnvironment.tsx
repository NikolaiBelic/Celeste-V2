import {
  Environment,
  Lightformer,
} from "@react-three/drei";

interface CrystalEnvironmentProps {
  accentColor: string;
}

export function CrystalEnvironment({
  accentColor,
}: CrystalEnvironmentProps) {
  return (
    <Environment
      resolution={256}
      background={false}
    >
      {/*
       * REFLECTOR SUPERIOR FRÍO
       *
       * Grande pero no extremadamente intenso.
       * Revela las facetas superiores con tonos
       * gris/plata en lugar de calentarlas.
       */}
      <Lightformer
        form="rect"
        color="#c8d0da"
        intensity={1.8}
        position={[0, 4, -1]}
        rotation={[Math.PI / 2, 0, 0]}
        scale={[5, 2, 1]}
      />

      {/*
       * REFLECTOR PRINCIPAL IZQUIERDO
       *
       * Es la fuente principal para conseguir
       * superficies gris humo y acero.
       */}
      <Lightformer
        form="rect"
        color="#8994a2"
        intensity={2.1}
        position={[-4, 0.4, 1.5]}
        rotation={[0, Math.PI / 2, 0]}
        scale={[3.4, 5.2, 1]}
      />

      {/*
       * HIGHLIGHT BLANCO PEQUEÑO
       *
       * Produce unas pocas facetas claramente
       * plateadas/blancas.
       */}
      <Lightformer
        form="rect"
        color="#eef2f6"
        intensity={2.6}
        position={[1.2, 2.2, 4]}
        rotation={[0, 0, 0]}
        scale={[1.15, 0.55, 1]}
      />

      {/*
       * REFLECTOR DERECHO OSCURO
       *
       * Revela geometría sin sacar las caras
       * demasiado lejos del negro.
       */}
      <Lightformer
        form="rect"
        color="#343a43"
        intensity={1.25}
        position={[4, 0.1, 0.8]}
        rotation={[0, -Math.PI / 2, 0]}
        scale={[2.8, 4.4, 1]}
      />

      {/*
       * CONTRALUZ FRÍO TRASERO
       *
       * Introduce reflejos estrechos en los
       * contornos y algunas caras oblicuas.
       */}
      <Lightformer
        form="rect"
        color="#657180"
        intensity={1.35}
        position={[-1.8, 1, -4]}
        rotation={[0, Math.PI, 0]}
        scale={[2, 3.5, 1]}
      />

      {/*
       * ACENTO NARANJA
       *
       * Mucho más pequeño y débil que antes.
       * Su trabajo es introducir algún reflejo
       * cobre aislado, no colorear la esfera.
       */}
      <Lightformer
        form="rect"
        color={accentColor}
        intensity={0.55}
        position={[3.2, -1.1, 3]}
        rotation={[0, -0.7, -0.15]}
        scale={[0.16, 2.1, 1]}
      />

      {/*
       * RELLENO INFERIOR OSCURO Y NEUTRO.
       */}
      <Lightformer
        form="rect"
        color="#20242a"
        intensity={0.65}
        position={[0, -4, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        scale={[4, 2, 1]}
      />
    </Environment>
  );
}
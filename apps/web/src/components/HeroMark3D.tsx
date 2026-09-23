"use client";

import { Center, Float, Text3D } from "@react-three/drei";
import { Canvas, useFrame, type ThreeElements } from "@react-three/fiber";
import { Suspense, useRef } from "react";
import type { Group } from "three";

/* eslint-disable @typescript-eslint/no-namespace, @typescript-eslint/no-empty-object-type */
declare module "react" {
  namespace JSX {
    interface IntrinsicElements extends ThreeElements {}
  }
}
/* eslint-enable @typescript-eslint/no-namespace, @typescript-eslint/no-empty-object-type */

function Mark() {
  const group = useRef<Group>(null);

  useFrame((state) => {
    if (!group.current) return;
    const x = state.pointer.x * 0.35;
    const y = state.pointer.y * 0.2;
    group.current.rotation.y += (x - group.current.rotation.y) * 0.06;
    group.current.rotation.x += (-y - group.current.rotation.x) * 0.06;
  });

  return (
    <Float speed={1.4} rotationIntensity={0.18} floatIntensity={0.45}>
      <group ref={group}>
        <Center>
          <Text3D
            font="/fonts/helvetiker_regular.typeface.json"
            size={0.82}
            height={0.28}
            curveSegments={10}
            bevelEnabled
            bevelThickness={0.03}
            bevelSize={0.02}
            bevelSegments={4}
          >
            afrosite
            <meshStandardMaterial color="#C1502E" roughness={0.28} metalness={0.22} />
          </Text3D>
        </Center>
      </group>
    </Float>
  );
}

export function HeroMark3D() {
  return (
    <div className="hero3d" aria-label="Afrosite 3D">
      <Canvas
        camera={{ position: [0, 0, 4.2], fov: 38 }}
        dpr={[1, 1.75]}
        gl={{ alpha: true, antialias: true }}
      >
        <ambientLight intensity={0.85} />
        <directionalLight position={[3, 4, 6]} intensity={1.35} color="#FBF4EC" />
        <directionalLight position={[-4, -1, 2]} intensity={0.55} color="#C1502E" />
        <Suspense fallback={null}>
          <Mark />
        </Suspense>
      </Canvas>
    </div>
  );
}

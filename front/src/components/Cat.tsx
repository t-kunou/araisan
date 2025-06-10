import React, {useRef} from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import {useGLTF, OrbitControls} from '@react-three/drei';
import * as THREE from 'three';


function Model({ modelPath }: { modelPath: string }) {
  const { scene } = useGLTF(modelPath);

  return (
    <primitive object={scene} dispose={null} position={[0, -1, 0]} scale={0.5}/>
  );
}


function Animation() {
  const meshRef = useRef<THREE.Mesh>(null!);

  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.x += delta * 0.2;
      meshRef.current.rotation.y += delta * 0.25;
    }
  });

  return null;
}



const CatModel: React.FC<{modelPath: string}> =({modelPath}) => {
  return (
    <Canvas camera={{ position: [0, 1, 3] }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[0, 5, 5]} />
      <Model modelPath={modelPath} />
      <OrbitControls />
      <Animation />
    </Canvas>
  );
};

export default CatModel;

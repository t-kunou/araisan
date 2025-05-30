import type { NextPage } from "next";
import Cat from '@/components/Cat';
import { speakText, speachToText } from '@/components/VoiceOperation';

const Home: NextPage = () => {
  async function handleClick() {
    //return;
    speakText('音声入力を開始します');
    await speachToText(
      (text: string) => {
        console.log(text);
        speakText(text);
      }
    );
    return;
  }

  return (
    <div>
      <h1>Three.js in Next.js</h1>
      <div style={{ width: '100%', height: '50vh' }} onClick={handleClick}>
        <Cat modelPath={'/models/cat/scene.gltf'} />
      </div>
    </div>
  )
};


export default Home;

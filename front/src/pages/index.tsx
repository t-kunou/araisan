import type { NextPage } from "next";
import Cat from '@/components/Cat';
import { speakText, speachToText } from '@/components/VoiceOperation';
import {  useEffect, useState } from "react";

const BACKGROUND_IMAGES = [
  'backgrounds/1.jpeg',
  'backgrounds/2.jpeg',
  'backgrounds/3.jpeg',
  'backgrounds/4.jpeg',
  'backgrounds/5.jpeg',
  'backgrounds/6.jpeg',
]

const USAGE_MESSAGE = `
おなかのあたりをクリックしてマイクに向かって話しかけてください。
なんにでも答えるけど、こんな質問は得意です！
- 「今日の天気は？」
- 「明日の夕飯は何が良い？」
- 「週末出かけるならどこが良い？」

マイクとスピーカーを使うよ。chromeで開いてね。chrome以外の挙動はよくわからないよ。
`;

const Home: NextPage = () => {
  //const [loggedIn, setLoggedIn] = useState(false);
  const [responseText, setResponseText] = useState(USAGE_MESSAGE);
  const [thinking, setThinking] = useState(false);
  const [background, setBackground] = useState(BACKGROUND_IMAGES[0]);
  const [recording, setRecording] = useState(false);

  const [location] = useState(process.env.NEXT_PUBLIC_LOCATION); // 初期値を設定

  useEffect(() => {
    const randomBg = BACKGROUND_IMAGES[Math.floor(Math.random() * BACKGROUND_IMAGES.length)];
    setBackground(randomBg);
  }
  , []);

  // useEffect(() => {
  //   async function checkAuth() {
  //     const res = await fetch(process.env.NEXT_PUBLIC_API_BASE_URL + '/check_auth', {
  //       credentials: 'include',
  //     });
  //     const data = await res.json();
  //     setLoggedIn(data.authenticated);
  //   }
  //   checkAuth();
  // }, []);

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  async function handleClick() {
    setRecording(true);
    await speachToText(
      async (text: string) => {
        setRecording(false);
        if (thinking || !text) {
          return; 
        }
        const url = apiBaseUrl + '/agent_request';
        console.log('Sending request to:', url);
        console.log(text);
        setResponseText(`「${text}」について考え中……`);
        setThinking(true);

        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            query: text,
            location: location,
          }),
          //credentials: 'include',
        })

        console.log('Response status:', response.status);
        if (response.ok) {
          const data = await response.json();
          console.log('Response data:', data);
          setResponseText(data.result);
          speakText(data.kana, () => {
            setResponseText(USAGE_MESSAGE)
          });
        } 
        setThinking(false);
      }
    );
    return;
  }

  return (
    <div
    >
      <h1>araisan app</h1>
        <div
            style={{
            minHeight: '100vh',
            backgroundImage: `url(${background})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            transition: 'background-image 0.5s',
          }}
        >
          <div
            style={{
              position: 'fixed',
              //center
              left: '10%',
              bottom: '50%',
              marginLeft: '2em',
              width: '80%'
             
            }}>
            <pre
              id="responseText"
              style={{
                whiteSpace: "pre-wrap",
                wordWrap: "break-word",
                marginLeft: '2em',
                marginRight: '2em',
                minHeight: '20em',
                fontSize: '1.2em',
                borderRadius: '1em',         // 角丸
                border: '4px solid #fff',    // 白い太線
                padding: '1em',              // 内側余白
                background: 'rgba(0,0,0,0.4)'// お好みで背景色
                }}>
              {responseText}
            </pre>
            <div
              style={{
                width: "0",
                height: "0",
                marginLeft: "30%", // 中央に配置
                borderLeft: "50px solid transparent",
                borderRight: "50px solid transparent",
                borderTop: "100px solid",
                color: 'rgba(255, 255, 255, 1)',
              }}
            />
          </div>
          <div style={{ width: '100%', height: '50vh', bottom: '2em', position: 'fixed' }} onClick={handleClick}>
            <Cat modelPath={'/models/cat/scene.gltf'} />
          </div>
          { recording ? (
            <div style={{ position: 'fixed', bottom: '1em', left: '50%', transform: 'translateX(-50%)', backgroundColor: 'rgba(255, 0, 0, 0.7)', color: '#faa', padding: '0.5em 1em', borderRadius: '0.5em' }}>
              <p>音声を認識中...</p>
            </div>
          ) : (
            <div style={{ position: 'fixed', bottom: '1em', left: '50%', transform: 'translateX(-50%)', backgroundColor: 'rgba(0, 0, 0, 0.7)', color: '#fff', padding: '0.5em 1em', borderRadius: '0.5em' }}>
              <p>クリックしてください</p>
            </div>
          )}
        </div>
    </div>
  )
};


export default Home;

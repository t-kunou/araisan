const prioriticalVoices = [
  'Microsoft Ichiro - Japanese (Japan)',
  'Google 日本語',
]

export function speakText(text: string, onEnd?: () => void): void {
  console.log('speakText', text);
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'ja-JP'; // Set the language to Japanese

  const voices = window.speechSynthesis.getVoices();
  console.log(voices.filter(v => v.lang === 'ja-JP'));
  if (voices.length === 0) {
    console.warn('No voices available');
    return;
  }

  const voice = voices.find(v => prioriticalVoices.includes(v.voiceURI));

  utterance.voice = voice || voices[0]; // Fallback to the first available voice
  console.log(utterance.voice);

  utterance.rate = 2.0;
  utterance.pitch = 1.2;

  if (onEnd) {
    utterance.onend = onEnd;
  }

  window.speechSynthesis.speak(utterance);
}

/* eslint-disable @typescript-eslint/no-explicit-any */
export async function speachToText(onend: (text: string) => void ): Promise<string> {
  if('webkitSpeechRecognition' in window) {
    const recognition = new (window as any).webkitSpeechRecognition();
    recognition.lang = 'ja-JP';
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    recognition.continuous = false; // TODO 終了検出を実装する

    let finalTranscript = '';
    recognition.onresult = (event: any) => {
      for (const result of event.results) {
        if (result.isFinal) {
          finalTranscript += result[0].transcript;
        }
      }

      if(finalTranscript.includes('終了')) {
        recognition.stop();
      }
    }

    console.log('開始')
    recognition.start();

    recognition.onend = () => {
      onend(finalTranscript);
    }

    return finalTranscript;
  }

  console.warn('Speech recognition not supported');
  return '';
}
/* eslint-enable @typescript-eslint/no-explicit-any */

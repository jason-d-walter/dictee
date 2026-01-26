import { useCallback, useEffect, useState } from 'react';

interface UseSpeechReturn {
  speak: (text: string) => void;
  speaking: boolean;
  supported: boolean;
}

export function useSpeech(): UseSpeechReturn {
  const [speaking, setSpeaking] = useState(false);
  const [supported, setSupported] = useState(true);

  useEffect(() => {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      setSupported(false);
    }
  }, []);

  const speak = useCallback((text: string) => {
    if (!window.speechSynthesis) {
      console.warn('Speech synthesis not supported');
      return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'fr-FR';
    utterance.rate = 0.8; // Slower for kids
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    // Try to find a French voice
    const voices = window.speechSynthesis.getVoices();
    const frenchVoice = voices.find(
      voice => voice.lang.startsWith('fr') && voice.localService
    ) || voices.find(
      voice => voice.lang.startsWith('fr')
    );

    if (frenchVoice) {
      utterance.voice = frenchVoice;
    }

    utterance.onstart = () => setSpeaking(true);
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);

    window.speechSynthesis.speak(utterance);
  }, []);

  return { speak, speaking, supported };
}

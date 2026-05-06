/**
 * Speech Recognition Module for INK Assistant
 * Optimized for reliability, error tolerance, and production performance.
 */

const LANG_MAP = {
  en: 'en-US',
  de: 'de-DE',
  fr: 'fr-FR',
  es: 'es-ES',
  ar: 'ar-SA'
};

export const checkMicPermission = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach(track => track.stop());
    return true;
  } catch (err) {
    console.error('Microphone permission denied:', err);
    return false;
  }
};

export const initializeSpeechRecognition = (onResult, onError, onStateChange, languageCode = 'en') => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    return { error: 'unsupported' };
  }

  const recognition = new SpeechRecognition();
  
  // Configuration per requirements
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = LANG_MAP[languageCode] || 'en-US';
  recognition.maxAlternatives = 1;

  let retryCount = 0;
  let silenceTimer = null;

  recognition.onstart = () => {
    onStateChange('listening');
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    const trimmed = transcript.trim().toLowerCase();

    // Noise/Silence handling: length < 2 or symbols only
    if (trimmed.length < 2 || /^[^a-zA-Z0-9\u0600-\u06FF]+$/.test(trimmed)) {
      console.warn('Noise-only input detected, ignoring.');
      return;
    }

    onStateChange('processing');
    onResult(trimmed);
    recognition.stop();
  };

  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
    
    // Auto-retry once on failure (except for permission/not-allowed)
    if (retryCount === 0 && (event.error === 'no-speech' || event.error === 'network' || event.error === 'audio-capture')) {
      retryCount++;
      console.log(`Auto-retrying recognition (Attempt ${retryCount})...`);
      setTimeout(() => {
        try {
          recognition.start();
        } catch (e) {
          onError(event.error);
        }
      }, 500);
      return;
    }

    onError(event.error);
    onStateChange('error');
    setTimeout(() => onStateChange('idle'), 3000);
  };

  recognition.onend = () => {
    onStateChange((current) => (current === 'listening' ? 'idle' : current));
  };

  return recognition;
};

export const startListeningService = async (recognition, onTimeout, onError) => {
  if (!recognition || recognition.error === 'unsupported') {
    onError('unsupported');
    return;
  }

  // Permission Rule
  const hasPermission = await checkMicPermission();
  if (!hasPermission) {
    onError('not-allowed');
    return;
  }

  try {
    recognition.start();
    
    // 5s listening timeout + 2s silence buffer implementation
    const timeoutId = setTimeout(() => {
      recognition.stop();
      onTimeout();
    }, 7000); // 5s + 2s buffer

    recognition.addEventListener('end', () => clearTimeout(timeoutId), { once: true });
    recognition.addEventListener('result', () => clearTimeout(timeoutId), { once: true });
    
  } catch (e) {
    console.error('Failed to start recognition:', e);
    // If already started, just ignore or reset
  }
};

export const stopListeningService = (recognition) => {
  if (recognition && typeof recognition.stop === 'function') {
    try {
      recognition.stop();
    } catch (e) {
      // recognition might already be stopped
    }
  }
};

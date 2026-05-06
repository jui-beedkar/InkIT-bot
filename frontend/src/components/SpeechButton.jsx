import React from "react";
import SpeechRecognition, {
    useSpeechRecognition,
} from "react-speech-recognition";

const SpeechButton = ({ onText }) => {
    const {
        transcript,
        listening,
        resetTranscript,
        browserSupportsSpeechRecognition,
    } = useSpeechRecognition();

    if (!browserSupportsSpeechRecognition) {
        return <span>Speech recognition not supported</span>;
    }

    const startListening = () => {
        resetTranscript();

        SpeechRecognition.startListening({
            continuous: false,
            language: "en-US",
        });
    };

    React.useEffect(() => {
        if (!listening && transcript) {
            onText(transcript);
        }
    }, [listening]);

    return (
        <button onClick={startListening}>
            {listening ? "Listening..." : "🎤"}
        </button>
    );
};

export default SpeechButton;
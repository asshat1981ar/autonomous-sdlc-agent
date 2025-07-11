import React, { useState, useRef, useEffect } from 'react';
import { Icons } from '../constants';

interface VoiceInteractionPanelProps {
    onVoiceCommand: (command: string) => void;
    isListening?: boolean;
    disabled?: boolean;
}

const VoiceInteractionPanel: React.FC<VoiceInteractionPanelProps> = ({
    onVoiceCommand,
    isListening = false,
    disabled = false
}) => {
    const [isRecording, setIsRecording] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [isSupported, setIsSupported] = useState(false);
    const recognitionRef = useRef<SpeechRecognition | null>(null);

    useEffect(() => {
        // Check if speech recognition is supported
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            setIsSupported(true);
            recognitionRef.current = new SpeechRecognition();
            
            const recognition = recognitionRef.current;
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onstart = () => {
                setIsRecording(true);
            };

            recognition.onresult = (event) => {
                let finalTranscript = '';
                let interimTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript;
                    } else {
                        interimTranscript += transcript;
                    }
                }

                setTranscript(finalTranscript || interimTranscript);

                if (finalTranscript) {
                    onVoiceCommand(finalTranscript);
                }
            };

            recognition.onend = () => {
                setIsRecording(false);
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                setIsRecording(false);
            };
        }

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop();
            }
        };
    }, [onVoiceCommand]);

    const startListening = () => {
        if (recognitionRef.current && !isRecording && !disabled) {
            setTranscript('');
            recognitionRef.current.start();
        }
    };

    const stopListening = () => {
        if (recognitionRef.current && isRecording) {
            recognitionRef.current.stop();
        }
    };

    const speakText = (text: string) => {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.8;
            utterance.pitch = 1;
            utterance.volume = 0.8;
            speechSynthesis.speak(utterance);
        }
    };

    if (!isSupported) {
        return (
            <div className="bg-gray-800/50 border border-gray-700 rounded-2xl shadow-lg p-6">
                <h3 className="text-xl font-bold text-white mb-4">Voice Interaction</h3>
                <p className="text-gray-400">
                    Voice recognition is not supported in your browser. Please use a modern browser like Chrome or Firefox.
                </p>
            </div>
        );
    }

    return (
        <div className="bg-gray-800/50 border border-gray-700 rounded-2xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-white mb-4">Voice Interaction</h3>
            
            <div className="space-y-4">
                {/* Voice Input Section */}
                <div className="flex items-center space-x-4">
                    <button
                        onClick={isRecording ? stopListening : startListening}
                        disabled={disabled}
                        className={`
                            flex items-center justify-center w-12 h-12 rounded-full transition-all duration-200
                            ${isRecording 
                                ? 'bg-red-600 hover:bg-red-500 animate-pulse' 
                                : 'bg-cyan-600 hover:bg-cyan-500'
                            }
                            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                            focus:outline-none focus:ring-4 focus:ring-cyan-400
                        `}
                        aria-label={isRecording ? 'Stop recording' : 'Start voice recording'}
                        aria-pressed={isRecording}
                    >
                        {isRecording ? (
                            <div className="w-4 h-4 bg-white rounded-sm" />
                        ) : (
                            <svg 
                                className="w-6 h-6 text-white" 
                                fill="none" 
                                stroke="currentColor" 
                                viewBox="0 0 24 24"
                                aria-hidden="true"
                            >
                                <path 
                                    strokeLinecap="round" 
                                    strokeLinejoin="round" 
                                    strokeWidth={2} 
                                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" 
                                />
                            </svg>
                        )}
                    </button>
                    
                    <div className="flex-1">
                        <div className="text-sm text-gray-400 mb-1">
                            {isRecording ? 'Listening...' : 'Click to start voice input'}
                        </div>
                        {transcript && (
                            <div className="text-white bg-gray-700 rounded p-2 text-sm">
                                "{transcript}"
                            </div>
                        )}
                    </div>
                </div>

                {/* Text-to-Speech Section */}
                <div className="border-t border-gray-700 pt-4">
                    <div className="flex items-center space-x-2 mb-2">
                        <Icons.User aria-label="Text to speech" />
                        <span className="text-sm text-gray-400">Text-to-Speech</span>
                    </div>
                    <div className="flex space-x-2">
                        <button
                            onClick={() => speakText('Welcome to the Autonomous SDLC Agent. How can I help you today?')}
                            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-400"
                            aria-label="Test text-to-speech"
                        >
                            Test TTS
                        </button>
                        <button
                            onClick={() => speechSynthesis.cancel()}
                            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-400"
                            aria-label="Stop speech"
                        >
                            Stop
                        </button>
                    </div>
                </div>

                {/* Voice Commands Help */}
                <div className="border-t border-gray-700 pt-4">
                    <details className="text-sm">
                        <summary className="text-gray-400 cursor-pointer hover:text-white">
                            Voice Commands
                        </summary>
                        <ul className="mt-2 space-y-1 text-gray-500">
                            <li>"Create a new project"</li>
                            <li>"Generate code for [filename]"</li>
                            <li>"Build the project"</li>
                            <li>"Show me the file tree"</li>
                            <li>"Explain this code"</li>
                        </ul>
                    </details>
                </div>
            </div>
        </div>
    );
};

export default VoiceInteractionPanel;


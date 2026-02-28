import React from 'react';
import { useState } from 'react';

interface SpeechInputProps {
  onSubmit: (speech: string) => Promise<void>;
  disabled: boolean;
  submitting: boolean;
}

export function SpeechInput({ onSubmit, disabled, submitting }: SpeechInputProps): React.JSX.Element {
  const [text, setText] = useState<string>('');

  const handleSubmit = async (): Promise<void> => {
    const trimmed = text.trim();
    if (!trimmed) return;
    await onSubmit(trimmed);
    setText('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      void handleSubmit();
    }
  };

  return (
    <div className="speech-input">
      <h3>Address Your Citizens</h3>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Deliver your speech as mayor... (Ctrl+Enter to submit)"
        disabled={disabled || submitting}
        rows={4}
      />
      <button
        onClick={() => void handleSubmit()}
        disabled={disabled || submitting || !text.trim()}
      >
        {submitting ? 'Delivering speech...' : 'Deliver Speech'}
      </button>
    </div>
  );
}

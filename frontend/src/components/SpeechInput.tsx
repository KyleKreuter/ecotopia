import React from 'react';
import { useState } from 'react';

interface SpeechInputProps {
  onSubmit: (speech: string) => Promise<void>;
  disabled: boolean;
  submitting: boolean;
}

const MAX_CHARS = 500;

const PLACEHOLDERS = [
  'Promise to invest in renewable energy and green jobs...',
  'Announce a new public transport initiative for the city...',
  'Address concerns about pollution near the industrial district...',
  'Propose a tax reform to fund ecological research...',
];

export function SpeechInput({ onSubmit, disabled, submitting }: SpeechInputProps): React.JSX.Element {
  const [text, setText] = useState<string>('');
  const [placeholder] = useState<string>(
    () => PLACEHOLDERS[Math.floor(Math.random() * PLACEHOLDERS.length)]
  );

  const charCount = text.length;
  const charClass = charCount >= MAX_CHARS ? 'at-limit' : charCount >= MAX_CHARS * 0.8 ? 'near-limit' : '';

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

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>): void => {
    if (e.target.value.length <= MAX_CHARS) {
      setText(e.target.value);
    }
  };

  return (
    <div className="speech-input">
      <h3>Address Your Citizens</h3>
      <p className="speech-hint">
        Make promises, announce policies, or respond to citizen concerns. Your words have consequences.
      </p>
      <div className="speech-textarea-wrapper">
        <textarea
          value={text}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled || submitting}
          rows={5}
        />
        <span className={`speech-char-count ${charClass}`}>
          {charCount}/{MAX_CHARS}
        </span>
      </div>
      <div className="speech-footer">
        <span className="speech-hint">Ctrl+Enter to submit</span>
        <button
          onClick={() => void handleSubmit()}
          disabled={disabled || submitting || !text.trim()}
        >
          {submitting && <span className="btn-spinner" />}
          {submitting ? 'Delivering...' : 'Deliver Speech'}
        </button>
      </div>
    </div>
  );
}

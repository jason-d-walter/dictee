export interface Word {
  id: string;
  text: string;
}

export interface WordProgress {
  wordId: string;
  correctStreak: number;
  totalAttempts: number;
  totalCorrect: number;
  lastPracticed: number;
  mastered: boolean;
}

export interface GameSession {
  mode: GameMode;
  words: Word[];
  currentIndex: number;
  stars: number;
  completed: boolean;
  results: WordResult[];
}

export interface WordResult {
  wordId: string;
  correct: boolean;
  attempts: number;
}

export type GameMode = 'audio-match' | 'lettres-perdues' | 'dictee-fantome';

export interface WordListData {
  words: Word[];
  createdAt: number;
  updatedAt: number;
}

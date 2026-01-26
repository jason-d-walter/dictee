import { Word, WordProgress, WordListData } from '../types';

const STORAGE_KEYS = {
  WORD_LIST: 'dictee_word_list',
  PROGRESS: 'dictee_progress',
} as const;

export function saveWordList(words: Word[]): void {
  const data: WordListData = {
    words,
    createdAt: Date.now(),
    updatedAt: Date.now(),
  };
  localStorage.setItem(STORAGE_KEYS.WORD_LIST, JSON.stringify(data));
}

export function loadWordList(): Word[] {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.WORD_LIST);
    if (!data) return [];
    const parsed: WordListData = JSON.parse(data);
    return parsed.words || [];
  } catch {
    return [];
  }
}

export function saveProgress(progress: Record<string, WordProgress>): void {
  localStorage.setItem(STORAGE_KEYS.PROGRESS, JSON.stringify(progress));
}

export function loadProgress(): Record<string, WordProgress> {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.PROGRESS);
    if (!data) return {};
    return JSON.parse(data);
  } catch {
    return {};
  }
}

export function clearAllData(): void {
  localStorage.removeItem(STORAGE_KEYS.WORD_LIST);
  localStorage.removeItem(STORAGE_KEYS.PROGRESS);
}

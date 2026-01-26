import { useState, useEffect, useCallback } from 'react';
import { Word, WordProgress } from '../types';
import { loadProgress, saveProgress } from '../utils/storage';
import { shuffleArray } from '../utils/wordUtils';

const MASTERY_THRESHOLD = 3; // Correct streak needed for mastery

interface UseProgressReturn {
  progress: Record<string, WordProgress>;
  recordAttempt: (wordId: string, correct: boolean) => void;
  getWordsForPractice: (words: Word[], limit: number) => Word[];
  resetProgress: () => void;
  getMasteryCount: (words: Word[]) => number;
}

export function useProgress(): UseProgressReturn {
  const [progress, setProgress] = useState<Record<string, WordProgress>>({});

  useEffect(() => {
    const loaded = loadProgress();
    setProgress(loaded);
  }, []);

  const recordAttempt = useCallback((wordId: string, correct: boolean) => {
    setProgress(prev => {
      const existing = prev[wordId] || {
        wordId,
        correctStreak: 0,
        totalAttempts: 0,
        totalCorrect: 0,
        lastPracticed: 0,
        mastered: false,
      };

      const newStreak = correct ? existing.correctStreak + 1 : 0;
      const updated: WordProgress = {
        ...existing,
        correctStreak: newStreak,
        totalAttempts: existing.totalAttempts + 1,
        totalCorrect: existing.totalCorrect + (correct ? 1 : 0),
        lastPracticed: Date.now(),
        mastered: newStreak >= MASTERY_THRESHOLD,
      };

      const newProgress = { ...prev, [wordId]: updated };
      saveProgress(newProgress);
      return newProgress;
    });
  }, []);

  const getWordsForPractice = useCallback(
    (words: Word[], limit: number): Word[] => {
      if (words.length === 0) return [];

      // Sort words by priority: unmastered first, then by least recently practiced
      const sortedWords = [...words].sort((a, b) => {
        const progressA = progress[a.id];
        const progressB = progress[b.id];

        // Unpracticed words first
        if (!progressA && progressB) return -1;
        if (progressA && !progressB) return 1;
        if (!progressA && !progressB) return 0;

        // Unmastered before mastered
        if (!progressA!.mastered && progressB!.mastered) return -1;
        if (progressA!.mastered && !progressB!.mastered) return 1;

        // Within same mastery status, prioritize least recently practiced
        return (progressA!.lastPracticed || 0) - (progressB!.lastPracticed || 0);
      });

      // Take up to limit words, shuffle them for variety
      const selected = sortedWords.slice(0, Math.min(limit, words.length));
      return shuffleArray(selected);
    },
    [progress]
  );

  const resetProgress = useCallback(() => {
    setProgress({});
    saveProgress({});
  }, []);

  const getMasteryCount = useCallback(
    (words: Word[]): number => {
      return words.filter(w => progress[w.id]?.mastered).length;
    },
    [progress]
  );

  return { progress, recordAttempt, getWordsForPractice, resetProgress, getMasteryCount };
}

import { useState, useEffect } from 'react';
import { Word } from '../types';
import { fetchWordsFromGoogleSheets } from '../utils/fetchWords';

interface UseWordListReturn {
  words: Word[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useWordList(): UseWordListReturn {
  const [words, setWords] = useState<Word[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWords = async () => {
    setLoading(true);
    setError(null);
    try {
      const fetchedWords = await fetchWordsFromGoogleSheets();
      setWords(fetchedWords);
    } catch (err) {
      setError('Failed to load words');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWords();
  }, []);

  return { words, loading, error, refetch: fetchWords };
}

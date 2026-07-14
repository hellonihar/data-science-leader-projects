import { useState, useCallback } from 'react';

let globalUserId = crypto.randomUUID();

export function useUserId() {
  const [userId] = useState(() => globalUserId);
  const setUserId = useCallback((id: string) => {
    globalUserId = id;
  }, []);
  return { userId, setUserId };
}

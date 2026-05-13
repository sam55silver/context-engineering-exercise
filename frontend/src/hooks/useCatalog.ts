import { useState, useEffect, useCallback } from "react";
import { Title } from "../api";
import { apiClient } from "./ApiClient";

type UseCatalogReturn = {
  titles: Title[];
  loading: boolean;
  error: Error | null;
  addToWatchlist: (titleId: number) => Promise<void>;
};

export function useCatalog(): UseCatalogReturn {
  const [titles, setTitles] = useState<Title[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    apiClient
      .fetchCatalog()
      .then(setTitles)
      .catch((err) => setError(err))
      .finally(() => setLoading(false));
  }, []);

  const addToWatchlist = useCallback(
    (titleId: number) => apiClient.addToWatchlist(titleId),
    []
  );

  return { titles, loading, error, addToWatchlist };
}

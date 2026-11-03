import { useQuery, useQueryClient } from '@tanstack/react-query';
import { API } from '../../core/api/endpoints';
import { useAuth } from '../../core/auth/useAuth';

export function useWallet() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const walletQuery = useQuery({
    queryKey: ['wallet-me', user?.id],
    queryFn: () => API.wallet.getMe(),
    enabled: !!user,
    staleTime: 30_000,
  });

  const transactionsQuery = useQuery({
    queryKey: ['wallet-transactions', user?.id],
    queryFn: () => API.wallet.getTransactions(20, 0),
    enabled: !!user,
    staleTime: 30_000,
  });

  const pricingQuery = useQuery({
    queryKey: ['wallet-pricing'],
    queryFn: () => API.wallet.getPricing(),
    staleTime: 300_000,
  });

  const invalidateWallet = () => {
    queryClient.invalidateQueries({ queryKey: ['wallet-me'] });
    queryClient.invalidateQueries({ queryKey: ['wallet-transactions'] });
  };

  return {
    wallet: walletQuery.data,
    balance: walletQuery.data?.balance ?? 0,
    totalEarned: walletQuery.data?.total_earned ?? 0,
    totalSpent: walletQuery.data?.total_spent ?? 0,
    isLoading: walletQuery.isLoading,
    isError: walletQuery.isError,
    transactions: transactionsQuery.data?.items ?? [],
    transactionsLoading: transactionsQuery.isLoading,
    pricing: pricingQuery.data,
    refetchWallet: walletQuery.refetch,
    refetchTransactions: transactionsQuery.refetch,
    invalidateWallet,
  };
}

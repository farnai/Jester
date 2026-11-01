import { useQuery } from '@tanstack/react-query';
import { API } from '../../core/api/endpoints';
import { useAuth } from '../../core/auth/useAuth';
import { HomeDailyEnergy } from './HomeDailyEnergy';
import { HomeDoDont } from './HomeDoDont';
import { HomePersonalInsights } from './HomePersonalInsights';
import { HomeNewPeople } from './HomeNewPeople';
import './home.css';
import './homeRebuild.css';

export function HomePage() {
  const { user } = useAuth();

  // 1. Daily Energy (Section 1 & 2)
  const daily = useQuery({
    queryKey: ['daily-energy', user?.id],
    queryFn: () => API.interpretations.getDailyEnergy('auto', 'ka'),
    enabled: !!user,
    staleTime: 60_000,
    retry: 1,
  });

  // 3. Personal Insights 7-layer Catalog (Section 3)
  const personalCatalog = useQuery({
    queryKey: ['personal-catalog', user?.id],
    queryFn: () => API.interpretations.getPersonalCatalog('ka'),
    enabled: !!user,
    staleTime: 120_000,
    retry: 1,
  });

  // 4. New People Discovery (Section 4) - Newest registered 18+ users
  const newPeople = useQuery({
    queryKey: ['discovery-newest', user?.id],
    queryFn: async () => {
      const res = await API.discovery.people({ order: 'newest', limit: 6 });
      return res.items || [];
    },
    enabled: !!user,
    staleTime: 30_000,
    retry: 1,
  });

  const hasBirthData = !!personalCatalog.data?.has_data;

  return (
    <main className="jester-home-container" lang="ka">
      <div className="jester-home-layout">
        {/* SECTION 1: დღის ენერგია (Daily Energy) */}
        <HomeDailyEnergy
          data={daily.data}
          isLoading={daily.isLoading}
          isError={daily.isError}
          hasBirthData={hasBirthData}
          onRetry={() => void daily.refetch()}
        />

        {/* SECTION 2: გააკეთე / მოერიდე (Do & Don't) */}
        <HomeDoDont
          doItems={daily.data?.do}
          dontItems={daily.data?.dont}
          isLoading={daily.isLoading}
          isError={daily.isError}
        />

        {/* SECTION 3: გაიცანი საკუთარი თავი (Personal Insights) */}
        <HomePersonalInsights
          catalog={personalCatalog.data}
          isLoading={personalCatalog.isLoading}
          isError={personalCatalog.isError}
          onRetry={() => void personalCatalog.refetch()}
        />

        {/* SECTION 4: ახალი ადამიანები (New People) */}
        <HomeNewPeople
          people={newPeople.data || []}
          isLoading={newPeople.isLoading}
          isError={newPeople.isError}
          onRetry={() => void newPeople.refetch()}
        />
      </div>
    </main>
  );
}

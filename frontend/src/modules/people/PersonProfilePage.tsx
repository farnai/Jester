import { useState } from 'react';
import { useParams, useSearchParams, Link, Navigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { API } from '../../core/api/endpoints';
import { useAuth } from '../../core/auth/useAuth';
import { Badge, Skeleton, ErrorState, PrivacySafeNotFoundState } from '../../shared/ui';
import { SocialIdentity } from './SocialIdentity';
import { ConnectionActions } from './ConnectionActions';
import './person-profile.css';

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function PersonProfilePage() {
  const { id = '' } = useParams<{ id: string }>();
  return UUID_REGEX.test(id) ? <PersonProfile key={id} targetId={id} /> : <Navigate to="/discover" replace />;
}

function PersonProfile({ targetId }: { targetId: string }) {
  const { user } = useAuth();
  const [params] = useSearchParams();
  const [detailsOpen, setDetailsOpen] = useState(false);
  const requestedReturn = params.get('returnTo') || '';
  const returnTo = requestedReturn === '/discover' || requestedReturn.startsWith('/discover?') ? requestedReturn : '/discover';
  const isSelf = user?.id === targetId;
  const profile = useQuery({ queryKey: ['profile', targetId], queryFn: () => API.profiles.getProfileById(targetId), retry: false });
  const connections = useQuery({ queryKey: ['connections'], queryFn: API.connections.list, refetchInterval: 15000 });
  const blocked = connections.data?.some(c => c.status === 'blocked' && (c.user_a_id === targetId || c.user_b_id === targetId));
  const preview = useQuery({
    queryKey: ['compare-preview', targetId],
    queryFn: () => API.interpretations.comparePreview({ target_user_id: targetId, locale: 'ka' }),
    enabled: !!profile.data && !profile.error && !isSelf && !blocked, retry: false,
  });
  const astro = useQuery({ queryKey: ['astrology', targetId], queryFn: () => API.astrology.getPersonSafeAstro(targetId), enabled: detailsOpen && !!profile.data && !profile.error && !blocked, retry: false });
  if (blocked || (profile.error && [403, 404].includes((profile.error as { statusCode?: number }).statusCode || 0))) return <PrivacySafeNotFoundState message="პროფილი ვერ მოიძებნა ან მიუწვდომელია." />;
  if (profile.error) return <ErrorState error={profile.error} />;
  if (profile.isPending) return <Skeleton width="100%" height="400px" borderRadius="24px" />;
  if (!profile.data) return null;
  const score = preview.data?.score;
  const hook = preview.data?.interpretation?.text;
  return <div className="social-page person-profile">
    <nav className="person-breadcrumb"><Link to={returnTo}>← აღმოჩენაზე დაბრუნება</Link>{isSelf && <Badge variant="brand">ეს თქვენი პროფილია</Badge>}</nav>
    <SocialIdentity profile={profile.data} connectionActions={!isSelf && <div className="person-connection-bar"><ConnectionActions target={targetId} name={profile.data.display_name || 'მომხმარებელი'} /></div>} />
    {!isSelf && <section className="person-preview">
      <div className="person-preview-heading"><div><p className="social-eyebrow">JESTER / პირველი ხედვა</p><h2>რა შეიძლება დაგაკავშიროთ</h2></div>{typeof score === 'number' && Number.isFinite(score) && <span className="person-score" title="სინასტრიული თანხვედრა">თანხვედრა <strong>{Math.round(score)}</strong></span>}</div>
      {preview.isPending ? <p role="status">წინასწარი ხედვა იტვირთება…</p> : preview.isError ? <p>წინასწარი ხედვა ვერ ჩაიტვირთა. <button onClick={() => preview.refetch()}>ხელახლა ცდა</button></p> : hook ? <p className="person-hook">{hook}</p> : <p>შედარების წინასწარი ხედვა ამჟამად მიუწვდომელია.</p>}
      <p className="social-note">ეს საუბრის დასაწყისია. სრული „ჩვენი კავშირი“ იხსნება კავშირის მიღების შემდეგ.</p>
    </section>}
    <details className="person-details" open={detailsOpen} onToggle={e => setDetailsOpen(e.currentTarget.open)}>
      <summary>ასტროლოგიური კონტექსტი</summary>
      {detailsOpen && (astro.isPending ? <p role="status">კონტექსტი იტვირთება…</p> : astro.isError ? <p>კონტექსტი მიუწვდომელია. <button onClick={() => astro.refetch()}>ხელახლა ცდა</button></p> : astro.data ? <div className="social-tags">{[["მზე", astro.data.sun_sign], ["მთვარე", astro.data.moon_sign], ["ასცენდენტი", astro.data.ascendant_sign], ["სტიქია", astro.data.element_primary], ["მოდალობა", astro.data.modality_primary]].filter(([,value]) => value).map(([label,value]) => <span key={label}>{label}: {value}</span>)}</div> : null)}
    </details>
  </div>;
}

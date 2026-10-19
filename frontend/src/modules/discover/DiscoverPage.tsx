import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useInfiniteQuery, useQuery } from '@tanstack/react-query';
import { API } from '../../core/api/endpoints';
import { useAuth } from '../../core/auth/useAuth';
import { CitySelector } from '../../shared/ui';
import { DiscoverSwipeCard } from './DiscoverSwipeCard';
import './discovery.css';

export const DiscoverPage = () => {
  const { user } = useAuth();
  const [params, setParams] = useSearchParams();
  const q = params.get('q') || '', city = params.get('city') || '', shared = params.get('shared') === '1';
  const [search, setSearch] = useState(q);
  const [filtersOpen, setFiltersOpen] = useState(() => window.innerWidth >= 1000);
  useEffect(() => { const media = window.matchMedia('(min-width: 1000px)'); const listener = () => setFiltersOpen(media.matches); media.addEventListener('change', listener); return () => media.removeEventListener('change', listener); }, []);
  const mode = params.get('view') === 'list' ? 'list' : 'deck';
  const activeId = params.get('person');
  const page = useInfiniteQuery({
    queryKey: ['discovery-deck', user?.id, q, city, shared],
    queryFn: ({ pageParam, signal }) => API.discovery.people({ q, city_id: city, shared_only: shared, after: pageParam || undefined }, signal),
    initialPageParam: '', getNextPageParam: last => last.next_cursor || undefined,
    enabled: !!user, refetchOnMount: 'always', refetchInterval: 30000, retry: 1, networkMode: 'always',
  });
  const connections = useQuery({ queryKey: ['connections'], queryFn: API.connections.list, refetchInterval: 15000 });
  const people = (page.data?.pages.flatMap(p => p.items) || []).filter((person, index, all) => all.findIndex(other => other.id === person.id) === index && !connections.data?.some(c => c.status === 'blocked' && (c.user_a_id === person.id || c.user_b_id === person.id)));
  const foundIndex = activeId ? people.findIndex(p => p.id === activeId) : 0;
  const activeIndex = Math.max(0, foundIndex);
  const exhausted = params.get('end') === '1';
  const person = exhausted ? undefined : people[activeIndex];
  const [announcement, setAnnouncement] = useState('');
  const patchParams = (values: Record<string,string>, reset = false) => {
    const next = new URLSearchParams(params);
    if (reset) { next.delete('person'); next.delete('end'); }
    Object.entries(values).forEach(([key,value]) => value ? next.set(key,value) : next.delete(key));
    setParams(next, { replace: true });
  };
  useEffect(() => {
    if (activeId && foundIndex === -1 && page.hasNextPage && !page.isFetching && !page.isFetchNextPageError) void page.fetchNextPage();
  }, [activeId, foundIndex, page.hasNextPage, page.isFetching, page.isFetchNextPageError]);
  const next = async () => {
    if (page.isFetching) return;
    if (people[activeIndex + 1]) patchParams({ person: people[activeIndex + 1].id });
    else if (page.hasNextPage) {
      const result = await page.fetchNextPage();
      if (result.isError) return;
      const items = result.data?.pages.flatMap(p => p.items) || [];
      const index = items.findIndex(item => item.id === person?.id);
      const following = items[index + 1];
      patchParams(following ? { person: following.id } : { end: '1' });
    } else patchParams({ end: '1' });
    setAnnouncement('შემდეგი ადამიანი');
  };
  const relation = connections.data?.find(c => c.user_a_id === person?.id || c.user_b_id === person?.id);
  const rightHint = relation?.status === 'accepted' ? 'საუბარი — ღილაკით' : relation?.status === 'pending' ? 'მოთხოვნა მოლოდინშია' : 'კავშირის დადასტურება';
  const socialCopy = relation?.status === 'accepted' ? ['უკვე დაკავშირებული ხართ', 'საუბრის გასაგრძელებლად გახსენი ჩატი.']
    : relation?.status === 'pending' ? relation.initiated_by === user?.id
      ? ['მოთხოვნა გაგზავნილია', 'საუბარი გაიხსნება, როცა მეორე ადამიანი მოთხოვნას მიიღებს.']
      : ['შენთან დაკავშირება სურს', 'მიიღე მოთხოვნა, თუ საუბრის დაწყება გსურს.']
    : ['ინტერესი საუბრის დასაწყისია.', 'კავშირის მოთხოვნა საუბრის მოწვევაა. ჩატი ორივე ადამიანის თანხმობით იხსნება.'];
  const returnTo = `/discover?${params}`;
  return <div className="discover-experience">
    <header className="discover-heading"><div><p className="discover-eyebrow">MORE PEOPLE</p><h1>აღმოაჩინე ადამიანები</h1></div><div className="discover-view-switch" aria-label="აღმოჩენის ხედი"><button aria-pressed={mode === 'deck'} onClick={() => patchParams({ view: '' })}>ბარათები</button><button aria-pressed={mode === 'list'} onClick={() => patchParams({ view: 'list' })}>სია</button></div></header>
    <div className="discover-layout">
      <aside className="discover-filters"><details open={filtersOpen} onToggle={e => setFiltersOpen(e.currentTarget.open)}><summary>ძიება და ფილტრები</summary><form onSubmit={e => { e.preventDefault(); patchParams({ q: search.trim() }, true); }}><label htmlFor="people-search">სახელით ძიება</label><input id="people-search" value={search} maxLength={80} onChange={e => setSearch(e.target.value)} placeholder="ვის ეძებ?" /><button type="submit">ძებნა</button></form>
        <CitySelector value={city || null} initialDisplayLabel={params.get('cityLabel') || ''} label="ქალაქი" onChange={c => patchParams({ city: c.city_id, cityLabel: c.display_name }, true)} onClear={() => patchParams({ city: '', cityLabel: '' }, true)} />
        <label className="discover-check"><input type="checkbox" checked={shared} onChange={e => patchParams({ shared: e.target.checked ? '1' : '' }, true)} /> საერთო ინტერესებით</label>
        <button onClick={() => { setSearch(''); setParams({}, { replace: true }); }}>ფილტრების გასუფთავება</button>
      </details><p className="discover-help" id="swipe-instructions">← შემდეგი ადამიანი<br/>→ {rightHint}<br/>ფოტოზე შეხება — სხვა ფოტო.<br/>შეგიძლია გამოიყენო ღილაკებიც.</p></aside>
      <section className="discover-center" aria-label="ადამიანების აღმოჩენა">
        <span className="discover-sr" role="status" aria-live="polite">{announcement}</span>
        {page.isPending || (activeId && foundIndex === -1 && page.hasNextPage && page.isFetching) ? <div className="discover-empty" role="status">ადამიანები იტვირთება…</div> : (page.isError && !page.data) ? <div className="discover-empty" role="alert"><p>პროფილები ვერ ჩაიტვირთა.</p><button onClick={() => page.refetch()}>ხელახლა ცდა</button></div> : mode === 'list' ? <div className="discover-list">
          {people.map(p => <article key={p.id}><h2>{p.display_name}</h2><p>{p.city || 'ქალაქი არ არის მითითებული'}</p><div className="discover-interest-tags">{p.interests.slice(0,3).map(i => <span key={i.id}>{i.name}</span>)}</div><p>{p.common_interest_ids.length > 0 ? `${p.common_interest_ids.length} საერთო ინტერესი` : ''}</p><Link to={`/people/${p.id}?returnTo=${encodeURIComponent(returnTo)}`}>სრული პროფილი →</Link><button onClick={() => patchParams({ view: '', person: p.id, end: '' })}>ბარათის ნახვა</button></article>)}
          {!people.length && <p>ამ ფილტრებით ადამიანები ვერ მოიძებნა.</p>}{page.hasNextPage && <button disabled={page.isFetching} onClick={() => page.fetchNextPage()}>მეტის ნახვა</button>}
        </div> : person ? <DiscoverSwipeCard rightHint={rightHint} person={person} nextPerson={people[activeIndex+1]} onNext={next} profileLink={`/people/${person.id}?returnTo=${encodeURIComponent(`/discover?${new URLSearchParams({ ...Object.fromEntries(params), person: person.id })}`)}`} /> : <div className="discover-empty"><h2>{exhausted ? 'ამ ეტაპზე სულ ეს იყო' : 'ჯერ ვერავინ მოიძებნა'}</h2><p>შემდეგზე გადასვლა ადამიანს არ ბლოკავს და უარყოფით შეფასებას არ ინახავს.</p><button onClick={() => { patchParams({ person: '', end: '' }); page.refetch(); }}>თავიდან დათვალიერება</button></div>}
        {page.isFetchNextPageError && <p role="alert">შემდეგი გვერდი ვერ ჩაიტვირთა. <button onClick={() => page.fetchNextPage()}>ხელახლა ცდა</button></p>}
      </section>
      <aside className="discover-context"><p className="discover-eyebrow">ერთი ნაბიჯით ახლოს</p><h2>{socialCopy[0]}</h2>{person?.bio ? <p className="discover-context-bio">{person.bio}</p> : !person && <p>შეცვალე ფილტრები ან დაათვალიერე სია.</p>}<p className="discover-note">{socialCopy[1]}</p></aside>
    </div>
  </div>;
};

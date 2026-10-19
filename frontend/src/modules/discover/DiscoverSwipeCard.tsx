import { useRef, useState, type PointerEvent, type CSSProperties } from 'react';
import { Link } from 'react-router-dom';
import type { DiscoveryDeckPerson } from '../../core/api/types';
import { ProfileImage } from '../../shared/ui/ProfileImage';
import { useAuth } from '../../core/auth/useAuth';
import { ConnectionActions } from '../people/ConnectionActions';

export function DiscoverSwipeCard({ person, nextPerson, onNext, profileLink, rightHint }: {
  person: DiscoveryDeckPerson; nextPerson?: DiscoveryDeckPerson; onNext: () => void; profileLink: string; rightHint: string;
}) {
  const { user } = useAuth();
  const hintKey = `jester:swipe-hint:${user?.id}`;
  const [hint, setHint] = useState(() => { try { return !localStorage.getItem(hintKey); } catch { return true; } });
  const dismissHint = () => { setHint(false); try { localStorage.setItem(hintKey,'seen'); } catch { /* Storage is optional. */ } };
  const [photoState, setPhotoState] = useState({ id: person.id, index: 0 });
  const photoIndex = photoState.id === person.id ? Math.min(photoState.index, Math.max(0, person.photos.length - 1)) : 0;
  const [confirmSignal, setConfirmSignal] = useState(0);
  const [drag, setDrag] = useState(0);
  const start = useRef<{ x: number; y: number; horizontal: boolean; cancelled: boolean } | null>(null);
  const switchPhoto = (direction: number) => setPhotoState({ id: person.id, index: (photoIndex + direction + person.photos.length) % Math.max(1, person.photos.length) });
  const end = (event: PointerEvent<HTMLDivElement>) => {
    const origin = start.current; start.current = null; setDrag(0);
    if (!origin || origin.cancelled) return;
    const dx = event.clientX - origin.x, dy = event.clientY - origin.y;
    if (Math.abs(dx) >= 65 && Math.abs(dx) > Math.abs(dy) * 1.5) {
      dismissHint();
      if (dx < 0) onNext(); else setConfirmSignal(value => value + 1);
    } else if (Math.abs(dx) < 10 && Math.abs(dy) < 10) {
      const bounds = event.currentTarget.getBoundingClientRect();
      switchPhoto(event.clientX < bounds.left + bounds.width / 2 ? -1 : 1);
    }
  };
  const interests = [...person.interests].sort((a,b) => Number(person.common_interest_ids.includes(b.id)) - Number(person.common_interest_ids.includes(a.id))).slice(0,3);
  return <article className="discover-swipe-card" data-person-id={person.id}>
    <div className="discover-photo" tabIndex={0} role="group" aria-label="ფოტო და სვაიპი" aria-describedby="swipe-instructions"
      onKeyDown={e => { if (e.key === 'ArrowLeft') { e.preventDefault(); onNext(); } if (e.key === 'ArrowRight') { e.preventDefault(); setConfirmSignal(n => n + 1); } }}
      onPointerDown={e => { if (!e.isPrimary || e.button !== 0) return; start.current = { x: e.clientX, y: e.clientY, horizontal: false, cancelled: false }; }}
      onPointerMove={e => {
        const origin = start.current; if (!origin || origin.cancelled) return;
        const dx = e.clientX - origin.x, dy = e.clientY - origin.y;
        if (!origin.horizontal && Math.abs(dy) > 12 && Math.abs(dy) >= Math.abs(dx)) { origin.cancelled = true; return; }
        if (Math.abs(dx) > 12 && Math.abs(dx) > Math.abs(dy) * 1.5) { origin.horizontal = true; e.currentTarget.setPointerCapture(e.pointerId); setDrag(Math.max(-90, Math.min(90, dx))); }
      }} onPointerUp={end} onPointerCancel={() => { start.current = null; setDrag(0); }}
      style={{ '--swipe-x': `${drag}px` } as CSSProperties}>
      {[person, ...(nextPerson ? [nextPerson] : [])].map((item, index) => <div className={`discover-photo-layer${index ? ' is-preload' : ''}`} key={item.id} aria-hidden={index ? true : undefined}>
        {(index ? item.photos[0] : item.photos[photoIndex]) ? <ProfileImage mediaSize="card" draggable={false} src={(index ? item.photos[0] : item.photos[photoIndex]).url} alt={index ? '' : `${item.display_name} — ფოტო ${photoIndex + 1}`} /> : <div className="discover-no-photo"><span>◎</span><p>ფოტო ჯერ არ არის</p></div>}
      </div>)}
      {!!person.photos.length && <div className="discover-photo-progress" aria-label={`ფოტო ${photoIndex + 1} / ${person.photos.length}`}>{person.photos.map((p,i) => <span key={p.id} className={i === photoIndex ? 'active' : ''} />)}</div>}
      {drag !== 0 && <span className="discover-drag-label">{drag < 0 ? 'შემდეგი' : rightHint}</span>}
      <div className="discover-photo-identity"><h2>{person.display_name}</h2>{person.city && <p>{person.same_city ? 'შენს ქალაქში · ' : ''}{person.city}</p>}</div>
    </div>
    {hint && <div className="discover-swipe-hint"><span>← გაასრიალე შემდეგი ადამიანისთვის</span><button aria-label="მინიშნების დახურვა" onClick={dismissHint}>×</button></div>}
    {person.photos.length > 1 && <div className="discover-photo-buttons"><button aria-label="წინა ფოტო" onClick={() => switchPhoto(-1)}>‹</button><span>{photoIndex + 1} / {person.photos.length}</span><button aria-label="შემდეგი ფოტო" onClick={() => switchPhoto(1)}>›</button></div>}
    <div className="discover-card-copy"><div className="discover-interest-tags">{interests.map(i => <span className={person.common_interest_ids.includes(i.id) ? 'shared' : ''} key={i.id}>{person.common_interest_ids.includes(i.id) ? '↔ ' : ''}{i.name}</span>)}</div>
      {!!person.common_interest_ids.length && <p className="discover-common">{person.common_interest_ids.length} საერთო ინტერესი</p>}
      {person.hook_observation?.text && <p className="discover-short-hook"><span>JESTER · </span>{person.hook_observation.text}</p>}
    </div>
    <div className="discover-card-actions"><button onClick={onNext} aria-label="შემდეგი ადამიანი">შემდეგი</button><Link to={profileLink}>პროფილი</Link><ConnectionActions key={person.id} target={person.id} name={person.display_name} confirmSignal={confirmSignal} compact /></div>
  </article>;
}

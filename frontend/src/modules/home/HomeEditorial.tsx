import { Link } from 'react-router-dom';
import { HomeAvatar, HomeIcon } from './HomeElements';
import portrait from '../../assets/registration/hero_portrait.jpg';
import secondPortrait from '../../assets/registration/hero_woman_highres.jpg';

/** Brand photography is decorative, never presented as a discoverable member. */
export function HomeEditorialHero({ name, avatarUrl, connectionCount, incomingCount }: { name: string; avatarUrl?: string | null; connectionCount?: number; incomingCount?: number }) {
  return (
    <header className="home-editorial-hero">
      <div className="home-hero-copy">
        <Link to="/me" className="home-hero-greeting">
          <HomeAvatar name={name} src={avatarUrl} />
          <span><small>შენი სივრცე</small><strong>გამარჯობა, {name}</strong></span>
          <HomeIcon />
        </Link>
        {connectionCount !== undefined && <div className="home-personal-context">
          <Link to="/connections">შენი წრე · {connectionCount} კავშირი</Link>
          {!!incomingCount && <Link to="/connections?tab=incoming">{incomingCount} ახალი მოთხოვნა <HomeIcon /></Link>}
        </div>}
        <h1>კარგი საუბარი<br />შემთხვევით<br /><em>არ იწყება.</em></h1>
        <p className="home-hero-description">გაიცანი საინტერესო ადამიანები.<br className="home-desktop-break" /> აღმოაჩინე, რა გაკავშირებთ.</p>
        <Link to="/discover" className="home-primary-link">აღმოაჩინე ადამიანები <HomeIcon /></Link>
      </div>
      <div className="home-hero-art" aria-hidden="true">
        <span className="home-art-blob" />
        <span className="home-art-orbit" />
        <img className="home-hero-portrait" src={portrait} alt="" fetchPriority="high" />
        <img className="home-hero-secondary" src={secondPortrait} alt="" />
        <span className="home-art-note">ყველაფერი<br />ერთი „გამარჯობით“<br />იწყება.</span>
        <span className="home-art-spark">✳</span>
        <span className="home-art-caption">ადამიანები. ინსაითები.<br /><b>ნამდვილი კავშირები.</b></span>
        <ConnectionMotif className="home-art-thread" />
      </div>
    </header>
  );
}

/** Two independent voices meeting on one thread; decorative, not a score. */
export function ConnectionMotif({ className = '' }: { className?: string }) {
  return <svg className={`home-connection-motif ${className}`} viewBox="0 0 120 80" fill="none" aria-hidden="true">
    <path d="M24 49c-24-31 10-55 33-27l13 19c19 27 53 5 30-20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    <path d="M21 43c-8 10-5 20 6 22m69-37c11-8 10-18 0-23" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    <circle cx="26" cy="44" r="6" fill="currentColor" />
    <circle cx="96" cy="26" r="6" fill="currentColor" />
  </svg>;
}

export function HomeQuickActions() {
  return (
    <nav className="home-quick-actions" aria-label="სწრაფი მოქმედებები">
      <a href="#home-daily"><span className="home-quick-icon"><HomeIcon kind="sparkles" /></span><span><strong>ჩემი ინსაითი</strong><small>შეხედე საკუთარ თავს</small></span></a>
      <Link to="/discover"><span className="home-quick-icon"><HomeIcon kind="compass" /></span><span><strong>ახალი ადამიანები</strong><small>გაიცანი უფრო ახლოს</small></span></Link>
      <Link to="/connections"><span className="home-quick-icon"><HomeIcon kind="people" /></span><span><strong>ჩემი კავშირები</strong><small>აღმოაჩინე თქვენი დინამიკა</small></span></Link>
      <Link to="/messages"><span className="home-quick-icon"><HomeIcon kind="message" /></span><span><strong>საუბრები</strong><small>გააგრძელე ნაცნობი ამბავი</small></span></Link>
    </nav>
  );
}

export function HomeInsightArt() {
  return <div className="home-insight-art" aria-hidden="true">
    <ConnectionMotif />
  </div>;
}

export function HomeConversationInvitation({ hasConnections }: { hasConnections: boolean }) {
  return (
    <aside className="home-conversation-invitation">
      <div className="home-invitation-label"><HomeIcon kind="message" /><span>საუბარი აქ იწყება</span></div>
      <h2>„ბოლოს რამ<br />გაგაკვირვა?“</h2>
      <p>{hasConnections ? 'აირჩიე არსებული საუბარი და გაუზიარე ეს კითხვა შენს თანამოსაუბრეს.' : 'გაიცანი ადამიანი. ორმხრივი კავშირი საუბრის დასაწყისია.'}</p>
      <Link to={hasConnections ? '/messages' : '/discover'} className="home-primary-link">
        {hasConnections ? 'აირჩიე საუბარი' : 'იპოვე თანამოსაუბრე'} <HomeIcon />
      </Link>
      <span className="home-invitation-doodle" aria-hidden="true">↗</span>
    </aside>
  );
}

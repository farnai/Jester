import { useEffect, useRef, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import logo from "../../assets/brand/JESTER_Logo_Stacked_Outlined.svg";
import panorama from "../../assets/registration/panorama-editorial-v2.png";
import brain from "../../assets/registration/icon_brain.svg";
import heart from "../../assets/registration/icon_heart.svg";
import spark from "../../assets/registration/icon_spark.svg";

export function RegistrationHeader() {
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <header className="registration-header">
      <Link to="/" className="registration-brand" aria-label="JESTER — მთავარი">
        {/* Two viewports of the existing outlined brand file; no redrawn paths. */}
        <svg viewBox="320 50 560 340" aria-hidden="true" className="registration-brand-hat">
          <image href={logo} width="1200" height="700" />
        </svg>
        <svg viewBox="240 430 720 150" aria-hidden="true" className="registration-brand-name">
          <image href={logo} width="1200" height="700" />
        </svg>
      </Link>
      <nav id="registration-navigation" className={`registration-navigation${menuOpen ? " is-open" : ""}`} aria-label="მთავარი ნავიგაცია">
        <a href="#registration-features" onClick={() => setMenuOpen(false)}>როგორ მუშაობს</a>
        {/* These destinations do not exist in AppRoutes. Keep their reference labels
            non-interactive until approved URLs are supplied. */}
        <span aria-disabled="true">ჩვენ შესახებ</span>
        <span aria-disabled="true">ბლოგი</span>
        <Link className="registration-mobile-login" to="/auth/login">შესვლა</Link>
      </nav>
      <Link className="registration-header-login" to="/auth/login">შესვლა</Link>
      <button className="registration-menu-toggle" type="button" aria-label="მენიუ" aria-expanded={menuOpen} aria-controls="registration-navigation" onClick={() => setMenuOpen(!menuOpen)}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
          <path d={menuOpen ? "M6 6l12 12M6 18L18 6" : "M4 6h16M4 12h16M4 18h16"} />
        </svg>
      </button>
    </header>
  );
}

const skyBodies = [
  { name: 'saturn', x: 710, y: 115, radius: 14, light: '#eee0b9', dark: '#937956' },
  { name: 'moon', x: 400, y: 65, radius: 13, light: '#f0eee4', dark: '#858681' },
  { name: 'mercury', x: 125, y: 125, radius: 8, light: '#d2c6b4', dark: '#716c65' },
  { name: 'venus', x: 290, y: 250, radius: 11, light: '#f4dba8', dark: '#b88a56' },
  { name: 'mars', x: 535, y: 235, radius: 10, light: '#e6b096', dark: '#a45038' },
  { name: 'jupiter', x: 755, y: 310, radius: 18, light: '#ead2ae', dark: '#98745a' },
  { name: 'uranus', x: 565, y: 60, radius: 11, light: '#d1e8e4', dark: '#74a5aa' },
  { name: 'neptune', x: 80, y: 320, radius: 10, light: '#a6c7df', dark: '#476d9d' },
  { name: 'pluto', x: 420, y: 330, radius: 7, light: '#dec8b4', dark: '#8d7567' },
];

export function RegistrationScenery() {
  const scenery = useRef<HTMLDivElement>(null);
  const landscape = useRef<HTMLImageElement>(null);
  const [sky, setSky] = useState({ height: 780, sunset: 580, people: [[246, 690], [314, 705]] });
  useEffect(() => {
    const container = scenery.current;
    const img = landscape.current;
    if (!container || !img) return;
    const measure = () => {
      if (!img.naturalWidth) return;
      const box = container.getBoundingClientRect();
      const frame = img.getBoundingClientRect();
      if (!box.width) return;
      const scale = Math.max(frame.width / img.naturalWidth, frame.height / img.naturalHeight);
      const position = getComputedStyle(img).objectPosition.split(' ').map(value => parseFloat(value) / 100);
      const x = frame.left - box.left + (frame.width - img.naturalWidth * scale) * position[0];
      const y = frame.top - box.top + (frame.height - img.naturalHeight * scale) * position[1];
      const unit = 1200 / box.width;
      // Head positions in the unchanged panorama, accounting for its responsive cover crop.
      setSky({ height: box.height * unit, sunset: (y + img.naturalHeight * scale * .5) * unit, people: [[.205, .55], [.262, .59]].map(([px, py]) =>
        [(x + img.naturalWidth * scale * px) * unit, (y + img.naturalHeight * scale * py) * unit]) });
    };
    const observer = new ResizeObserver(measure);
    observer.observe(container);
    observer.observe(img);
    img.addEventListener('load', measure);
    measure();
    return () => { observer.disconnect(); img.removeEventListener('load', measure); };
  }, []);
  const connections = [
    { d: `M1210 ${sky.sunset} C1170 ${sky.sunset - 80} 1200 100 1120 30 S850 10 710 115`, delay: 0 },
    ...skyBodies.slice(1).map((body, index) => {
      const previous = skyBodies[index];
      return { d: `M${previous.x} ${previous.y} Q${(previous.x + body.x) / 2} ${Math.min(previous.y, body.y) - 35} ${body.x} ${body.y}`, delay: (index + 1) * 1.2 };
    }),
    ...sky.people.map(([x, y], i) => ({ d: `M420 330 Q${350 + i * 40} ${y - 95} ${x} ${y}`, delay: 10.8, person: true })),
  ];
  return (
    <div className="registration-scenery" aria-hidden="true" ref={scenery}>
      <svg className="registration-cosmos" viewBox={`0 0 1200 ${sky.height}`} fill="none" focusable="false">
        <defs>
          {skyBodies.map(body => <radialGradient key={body.name} id={`registration-${body.name}-surface`} cx="70%" cy="70%" r="85%">
            <stop stopColor={body.light} /><stop offset=".5" stopColor={body.light} /><stop offset="1" stopColor={body.dark} />
          </radialGradient>)}
          {skyBodies.map(body => <clipPath key={body.name} id={`registration-${body.name}-clip`}><circle r={body.radius} /></clipPath>)}
          <radialGradient id="registration-night" cx="75%" cy="65%" r="80%">
            <stop offset=".4" stopColor="#292631" stopOpacity="0" /><stop offset="1" stopColor="#292631" stopOpacity=".5" />
          </radialGradient>
        </defs>
        {/* Decorative connections, unrelated to calculated astrology or user data. */}
        <g className="registration-connections" stroke="#cb9962" strokeWidth="1.2" strokeLinecap="round">
          {connections.map(({ d, delay, ...connection }, index) => <g key={index} className={'person' in connection ? 'registration-person-connection' : undefined} style={{ '--connection-delay': `${delay}s` } as CSSProperties}>
            <path className="registration-link" d={d} pathLength="1" />
            <path className="registration-traveler" d={d} pathLength="1" stroke="#e3ab57" strokeWidth="2.5" />
          </g>)}
        </g>
        {skyBodies.map((body, index) => <g key={body.name} transform={`translate(${body.x} ${body.y})`} data-body={body.name}>
          <g className={`registration-planet${body.x < 440 ? ' registration-planet-behind-copy' : ''}`} style={{ animationDelay: `${index * 1.2}s` }}>
            {body.name === 'saturn' && <ellipse rx="27" ry="8" transform="rotate(-25)" stroke="#b4a080" strokeWidth="4" />}
            <circle r={body.radius} fill={`url(#registration-${body.name}-surface)`} />
            <g clipPath={`url(#registration-${body.name}-clip)`}>
              {['jupiter', 'saturn', 'venus'].includes(body.name) && <g fill="none" stroke={body.dark} opacity=".5">
                <path d="M-22-9Q0-4 22-8M-22 1Q0 6 22 0M-22 11Q0 15 22 9" strokeWidth={body.name === 'jupiter' ? 4 : 2} />
                <path d="M-22-3Q0 2 22-3M-22 7Q0 10 22 5" stroke={body.light} strokeWidth="2" />
              </g>}
              {['moon', 'mercury', 'mars', 'pluto'].includes(body.name) && <g fill={body.dark} opacity=".4">
                <circle cx="-4" cy="-3" r="3" /><circle cx="5" cy="3" r="2" /><circle cx="-2" cy="7" r="1.5" />
                <path d="M-10 0Q-5 1-6 6L-1 4 0-1-5-5Z" />
              </g>}
              {body.name === 'mars' && <ellipse cy="-9" rx="4" ry="2" fill="#f6e6d4" />}
              {body.name === 'jupiter' && <ellipse cx="7" cy="6" rx="4" ry="2" fill="#b47c60" />}
              {body.name === 'neptune' && <path d="M-12 3Q0 7 12 2" stroke="#bfd8e9" strokeWidth="2" opacity=".6" />}
              {body.name === 'pluto' && <path d="M0-1C-4-6-7 0 0 5 7 1 6-5 0-1" fill="#f2dfcb" />}
              <circle r={body.radius} fill="url(#registration-night)" />
            </g>
            {body.name === 'saturn' && <path d="M-24 12Q2 9 24-12" stroke="#c7b391" strokeWidth="3" />}
            {body.name === 'uranus' && <ellipse rx="15" ry="4" transform="rotate(-65)" stroke="#9dbbb9" strokeWidth=".7" />}
          </g>
        </g>)}
        <g className="registration-arrivals">
          {sky.people.map(([cx, cy], index) => <circle key={index} cx={cx} cy={cy} r="9" stroke="#e6b777" strokeWidth="1.4" />)}
        </g>
      </svg>
      <div className="registration-panorama"><img src={panorama} alt="" ref={landscape} /></div>
      <div className="registration-sunset-glow" />
    </div>
  );
}

const features = [
  { icon: brain, title: "გაიცანი შენი თავი", description: "შეისწავლე შენი ღირებულებები, ემოციები და კომუნიკაციის სტილი." },
  { icon: heart, title: "აღმოაჩინე შესაფერისი ადამიანები", description: "იპოვე ადამიანები, რომლებიც იზიარებენ შენს ღირებულებებსა და ინტერესებს." },
  { icon: spark, title: "შეიგრძენი უფრო ღრმა კავშირები", description: "მიიღე პერსონალური ანალიზი და ინსაიტები ურთიერთობების შესახებ." },
];

export function RegistrationStory() {
  return (
    <section className="registration-story" aria-labelledby="registration-headline">
      <h1 id="registration-headline">შექმენი თავი.<br />შექმენი სხვა.<br /><span>შეიგრძენი კავშირი.</span></h1>
      <p className="registration-intro">JESTER გეხმარება გაიგო შენი თავი, აღმოაჩინო სხვა ადამიანები და უკეთ გაიგო ნამდვილი, ღრმა კავშირები.</p>
      <div className="registration-features" id="registration-features">
        {features.map(({ icon, title, description }) => (
          <div className="registration-feature" key={title}>
            <img src={icon} alt="" width="72" height="72" />
            <div><h2>{title}</h2><p>{description}</p></div>
          </div>
        ))}
      </div>
    </section>
  );
}

export function RegistrationIcon({ kind }: { kind: "email" | "lock" | "eye" | "eye-off" }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {kind === "email" ? <><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 7 9 6 9-6" /></> : kind === "lock" ? <><rect x="5" y="10" width="14" height="11" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3" /></> : <><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7S2 12 2 12Z" /><circle cx="12" cy="12" r="3" />{kind === "eye-off" && <path d="m3 3 18 18" />}</>}
    </svg>
  );
}

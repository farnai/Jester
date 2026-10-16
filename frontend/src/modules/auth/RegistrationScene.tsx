import { useState } from "react";
import { Link } from "react-router-dom";
import logo from "../../assets/brand/JESTER_Logo_Stacked_Outlined.svg";
import portrait from "../../assets/registration/hero_woman_highres.jpg";
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

export function RegistrationScenery() {
  return (
    <div className="registration-scenery" aria-hidden="true">
      <div className="registration-cream-arc" />
      <div className="registration-portrait"><img src={portrait} alt="" fetchPriority="high" /></div>
      <div className="registration-panorama"><img src={panorama} alt="" /></div>
      <div className="registration-foreground-curve" />
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

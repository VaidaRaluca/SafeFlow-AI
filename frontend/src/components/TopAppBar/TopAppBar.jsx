import styles from './TopAppBar.module.css';
import { useAuth } from '../../auth/AuthContext.jsx';

export default function TopAppBar({ title }) {
  const { user } = useAuth();
  const initials = (user?.full_name || user?.email || 'U')
    .split(/[\s@]/)
    .filter(Boolean)
    .slice(0, 2)
    .map((s) => s[0].toUpperCase())
    .join('');

  return (
    <header className={styles.bar}>
      <div className={styles.left}>
        <h1 className={styles.title}>{title}</h1>
      </div>
      <div className={styles.right}>
        <button type="button" className={styles.iconBtn} aria-label="Notifications">
          <span className="material-symbols-outlined">notifications</span>
        </button>
        <button type="button" className={styles.iconBtn} aria-label="Help">
          <span className="material-symbols-outlined">help</span>
        </button>
        <div className={styles.avatar} title={user?.email}>
          {initials}
        </div>
      </div>
    </header>
  );
}

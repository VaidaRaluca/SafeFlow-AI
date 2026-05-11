import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../../api/client';
import styles from './Evaluate.module.css';

const MIN_DURATION_MS = 1800;

export default function Evaluate() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(15);

  useEffect(() => {
    const start = Date.now();
    let mounted = true;

    const tick = setInterval(() => {
      setProgress((p) => Math.min(95, p + Math.random() * 10));
    }, 250);

    const evaluate = async () => {
      try {
        const tx = await api.transaction(id);
        const elapsed = Date.now() - start;
        if (elapsed < MIN_DURATION_MS) {
          await new Promise((r) => setTimeout(r, MIN_DURATION_MS - elapsed));
        }
        if (!mounted) return;
        const status = String(tx.status).toUpperCase();
        if (status === 'SETTLED' || status === 'APPROVED') {
          navigate(`/transactions/${id}/approved`, { replace: true });
        } else if (status === 'WARNED') {
          navigate(`/transactions/${id}/caution`, { replace: true });
        } else if (status === 'REJECTED') {
          navigate(`/transactions/${id}/blocked`, { replace: true });
        } else if (status === 'CANCELED') {
          navigate('/dashboard', { replace: true });
        } else {
          // Still pending - retry briefly
          setTimeout(evaluate, 800);
        }
      } catch (err) {
        if (mounted) setError(err.message || 'Could not load transaction.');
      }
    };

    evaluate();

    return () => {
      mounted = false;
      clearInterval(tick);
    };
  }, [id, navigate]);

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <div className={styles.shieldWrap}>
          <span className="material-symbols-outlined filled">shield</span>
        </div>
        <h1 className={styles.title}>Evaluating Transaction</h1>
        <div className={styles.statusPill}>
          <span className={styles.dot} />
          PENDING — SECURITY SCAN ACTIVE
        </div>
      </header>

      {error && <div className={styles.errorBanner}>{error}</div>}

      <section className={styles.grid}>
        <div className={styles.panel}>
          <div className={styles.panelHeader}>
            <span className="material-symbols-outlined">memory</span>
            <h3>AI Risk Scoring</h3>
            <span className={styles.percent}>{Math.round(progress)}%</span>
          </div>
          <ProgressBar label="Analyzing historical patterns" value={100} done />
          <ProgressBar
            label="Verifying origin & destination"
            value={progress > 60 ? 100 : Math.min(95, progress * 1.4)}
            done={progress > 60}
          />
          <ProgressBar
            label="Calculating final confidence score"
            value={progress}
            done={false}
          />
        </div>

        <div className={styles.panelCenter}>
          <div className={styles.spinner}>
            <span className="material-symbols-outlined">search</span>
          </div>
          <h3>Algorithmic Scan</h3>
          <p>Checking compliance lists and behavioural rules.</p>
        </div>
      </section>

      <p className={styles.footer}>
        SafeFlow AI processes millions of data points to ensure your financial
        security. Please do not close this window.
      </p>
    </main>
  );
}

function ProgressBar({ label, value, done }) {
  return (
    <div className={styles.progressRow}>
      <div className={styles.progressLabels}>
        <span className={done ? styles.labelDone : styles.label}>{label}</span>
        <span className={done ? styles.statusDone : styles.statusPending}>
          {done ? 'Complete' : 'In Progress'}
        </span>
      </div>
      <div className={styles.progressTrack}>
        <div
          className={styles.progressFill}
          style={{ width: `${Math.max(8, Math.min(100, value))}%` }}
        />
      </div>
    </div>
  );
}

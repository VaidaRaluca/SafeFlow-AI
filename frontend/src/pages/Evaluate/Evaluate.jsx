import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../../api/client';
import { formatCurrency } from '../../utils/format';
import styles from './Evaluate.module.css';

const MIN_DURATION_MS = 2200;

export default function Evaluate() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [tx, setTx] = useState(null);
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
        const data = await api.transaction(id);
        if (mounted) setTx(data);
        const elapsed = Date.now() - start;
        if (elapsed < MIN_DURATION_MS) {
          await new Promise((r) => setTimeout(r, MIN_DURATION_MS - elapsed));
        }
        if (!mounted) return;
        const status = String(data.status).toUpperCase();
        if (status === 'SETTLED' || status === 'APPROVED') {
          navigate(`/transactions/${id}/approved`, { replace: true });
        } else if (status === 'WARNED') {
          navigate(`/transactions/${id}/caution`, { replace: true });
        } else if (status === 'REJECTED') {
          navigate(`/transactions/${id}/blocked`, { replace: true });
        } else if (status === 'CANCELED') {
          navigate('/dashboard', { replace: true });
        } else {
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

  const handleCancel = async () => {
    try {
      await api.cancelPayment(id, { reason: 'Cancelled during evaluation.' });
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(err.message || 'Could not cancel transaction.');
    }
  };

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

      <section className={styles.summary}>
        <div className={styles.summaryAccent} />
        <div className={styles.summaryLeft}>
          <p className={styles.summaryLabel}>Transfer Details</p>
          <div className={styles.summaryReceiver}>
            <div className={styles.receiverAvatar}>
              <span className="material-symbols-outlined">account_balance</span>
            </div>
            <div>
              <h2>Receiver Account</h2>
              <p>
                {tx
                  ? `Acct ID ••${tx.receiver_id.slice(-4)}`
                  : 'Loading recipient…'}
              </p>
            </div>
          </div>
        </div>
        <div className={styles.summaryRight}>
          <p className={styles.summaryLabel}>Amount</p>
          <div className={styles.summaryAmount}>
            {tx ? formatCurrency(tx.amount, tx.currency) : '—'}
          </div>
          <p className={styles.summarySub}>
            {tx?.description || `Transfer (${tx?.currency || 'EUR'})`}
          </p>
        </div>
      </section>

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
            <svg viewBox="0 0 36 36" className={styles.spinnerSvg}>
              <path
                className={styles.spinnerTrack}
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
              />
              <path
                className={styles.spinnerProgress}
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                strokeDasharray="75, 100"
                strokeLinecap="round"
              />
            </svg>
            <span className="material-symbols-outlined">search</span>
          </div>
          <h3>Algorithmic Scan</h3>
          <p>Checking global watchlists and OFAC compliance.</p>
        </div>
      </section>

      <div className={styles.actions}>
        <button type="button" className={styles.btnGhost} onClick={handleCancel}>
          <span className="material-symbols-outlined">close</span>
          Cancel Transaction
        </button>
      </div>

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

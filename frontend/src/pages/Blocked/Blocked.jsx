import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../../api/client';
import { formatCurrency, formatDateTime } from '../../utils/format';
import styles from './Blocked.module.css';

export default function Blocked() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [tx, setTx] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .transaction(id)
      .then(setTx)
      .catch((err) => setError(err.message || 'Could not load transaction.'));
  }, [id]);

  const risk = tx?.risk_assessment;

  return (
    <main className={styles.page}>
      <div className={styles.iconWrap}>
        <span className="material-symbols-outlined filled">block</span>
      </div>

      <h1 className={styles.title}>Transaction Blocked</h1>
      <p className={styles.subtitle}>
        Our security system has prevented this transaction for your protection.
      </p>

      {error && <div className={styles.errorBanner}>{error}</div>}

      {tx && (
        <div className={styles.card}>
          <div className={styles.accent} />

          <div className={styles.amountSection}>
            <span className={styles.amountLabel}>Attempted Amount</span>
            <span className={styles.amountValue}>
              {formatCurrency(tx.amount, tx.currency)}
            </span>
          </div>

          <div className={styles.factors}>
            <h3>
              <span className="material-symbols-outlined">warning</span>
              Risk Factors Detected
            </h3>

            {risk ? (
              <>
                <Factor
                  label="Combined risk score"
                  value={`${Number(risk.combined_score).toFixed(2)} (${risk.risk_level})`}
                />
                <Factor
                  label="Rule-based score"
                  value={Number(risk.rule_score).toFixed(2)}
                />
                <Factor
                  label="Anomaly model score"
                  value={Number(risk.anomaly_score).toFixed(2)}
                />
              </>
            ) : (
              <p className={styles.note}>
                The transaction exceeded our acceptable risk threshold.
              </p>
            )}

            <div className={styles.meta}>
              <span>Ref: {tx.id.slice(0, 8).toUpperCase()}</span>
              <span>{formatDateTime(tx.created_at)}</span>
            </div>
          </div>
        </div>
      )}

      <div className={styles.actions}>
        <button className={styles.btnPrimary} onClick={() => navigate('/dashboard')}>
          Return to Dashboard
        </button>
        <button
          className={styles.btnGhost}
          onClick={() => navigate('/history')}
          type="button"
        >
          <span className="material-symbols-outlined">receipt_long</span>
          View History
        </button>
      </div>
    </main>
  );
}

function Factor({ label, value }) {
  return (
    <div className={styles.factor}>
      <div className={styles.factorIcon}>
        <span className="material-symbols-outlined">priority_high</span>
      </div>
      <div>
        <p className={styles.factorLabel}>{label}</p>
        <p className={styles.factorValue}>{value}</p>
      </div>
    </div>
  );
}

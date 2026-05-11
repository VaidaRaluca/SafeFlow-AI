import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../../api/client';
import { formatCurrency } from '../../utils/format';
import styles from './Caution.module.css';

export default function Caution() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [tx, setTx] = useState(null);
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    api
      .transaction(id)
      .then((t) => {
        setTx(t);
        const status = String(t.status).toUpperCase();
        if (status === 'SETTLED' || status === 'APPROVED') {
          navigate(`/transactions/${id}/approved`, { replace: true });
        } else if (status === 'REJECTED') {
          navigate(`/transactions/${id}/blocked`, { replace: true });
        } else if (status === 'CANCELED') {
          navigate('/dashboard', { replace: true });
        }
      })
      .catch((err) => setError(err.message || 'Could not load transaction.'));
  }, [id, navigate]);

  const handleConfirm = async (e) => {
    e.preventDefault();
    setError(null);
    if (!password) {
      setError('Please enter your password to confirm.');
      return;
    }
    setSubmitting(true);
    try {
      await api.confirmPayment(id, { password });
      navigate(`/transactions/${id}/approved`, { replace: true });
    } catch (err) {
      setError(err.message || 'Could not confirm payment.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = async () => {
    setError(null);
    setCancelling(true);
    try {
      await api.cancelPayment(id, { reason: 'User cancelled at warning step.' });
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(err.message || 'Could not cancel payment.');
    } finally {
      setCancelling(false);
    }
  };

  const risk = tx?.risk_assessment;

  return (
    <main className={styles.page}>
      <div className={styles.ambient} />

      <div className={styles.content}>
        <div className={styles.iconWrap}>
          <span className="material-symbols-outlined filled">warning</span>
        </div>

        <h1 className={styles.title}>Proceed Cautiously</h1>
        <p className={styles.subtitle}>
          Unusual activity detected. Please verify this transaction before it
          settles.
        </p>

        <div className={styles.card}>
          <div className={styles.riskBox}>
            <span className="material-symbols-outlined">info</span>
            <div>
              <h3>Risk Indicator</h3>
              <p>
                {risk
                  ? `Combined risk score ${Number(risk.combined_score).toFixed(
                      2
                    )} (level ${risk.risk_level}). Verify the recipient and amount before continuing.`
                  : 'Our scoring system flagged this transaction. Verify the recipient and amount before continuing.'}
              </p>
            </div>
          </div>

          {tx && (
            <div className={styles.summary}>
              <div className={styles.summaryRow}>
                <span>Transfer Amount</span>
                <strong>{formatCurrency(tx.amount, tx.currency)}</strong>
              </div>
              <div className={styles.summaryRow}>
                <span>Transaction ID</span>
                <code>{tx.id.slice(0, 8)}…</code>
              </div>
              {tx.description && (
                <div className={styles.summaryRow}>
                  <span>Description</span>
                  <span>{tx.description}</span>
                </div>
              )}
            </div>
          )}

          {error && <div className={styles.errorBanner}>{error}</div>}

          <form onSubmit={handleConfirm} className={styles.form}>
            <label htmlFor="password" className={styles.label}>
              Account Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={styles.input}
              placeholder="Enter your password to authorize"
              required
            />

            <div className={styles.actions}>
              <button
                type="submit"
                className={styles.btnPrimary}
                disabled={submitting || cancelling}
              >
                {submitting ? 'Confirming…' : 'Confirm & Settle'}
              </button>
              <button
                type="button"
                className={styles.btnGhost}
                onClick={handleCancel}
                disabled={submitting || cancelling}
              >
                {cancelling ? 'Cancelling…' : 'Cancel Transaction'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>
  );
}

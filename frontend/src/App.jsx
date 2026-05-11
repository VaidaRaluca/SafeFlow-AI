import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuth } from './auth/AuthContext.jsx';
import AppShell from './components/AppShell/AppShell.jsx';
import Login from './pages/Login/Login.jsx';
import Register from './pages/Register/Register.jsx';
import Dashboard from './pages/Dashboard/Dashboard.jsx';
import SendMoney from './pages/SendMoney/SendMoney.jsx';
import Evaluate from './pages/Evaluate/Evaluate.jsx';
import Approved from './pages/Approved/Approved.jsx';
import Caution from './pages/Caution/Caution.jsx';
import Blocked from './pages/Blocked/Blocked.jsx';
import History from './pages/History/History.jsx';

function RequireAuth({ children }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
}

function PublicOnly({ children }) {
  const { isAuthenticated } = useAuth();
  if (isAuthenticated) return <Navigate to="/dashboard" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicOnly>
            <Login />
          </PublicOnly>
        }
      />
      <Route
        path="/register"
        element={
          <PublicOnly>
            <Register />
          </PublicOnly>
        }
      />
      <Route
        element={
          <RequireAuth>
            <AppShell />
          </RequireAuth>
        }
      >
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/send" element={<SendMoney />} />
        <Route path="/history" element={<History />} />
      </Route>
      <Route
        path="/transactions/:id/evaluate"
        element={
          <RequireAuth>
            <Evaluate />
          </RequireAuth>
        }
      />
      <Route
        path="/transactions/:id/approved"
        element={
          <RequireAuth>
            <Approved />
          </RequireAuth>
        }
      />
      <Route
        path="/transactions/:id/caution"
        element={
          <RequireAuth>
            <Caution />
          </RequireAuth>
        }
      />
      <Route
        path="/transactions/:id/blocked"
        element={
          <RequireAuth>
            <Blocked />
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

import React, { useState, useEffect } from 'react';
import { 
  Rocket, Cloud, Activity, Package, Gamepad2, Video, Layout, Image, 
  Twitter, Rss, UserPlus, Settings, MessageSquare, Mail, Trophy,
  Plus, Trash2, Edit, Eye, EyeOff, Send, Sparkles, X, Check, AlertCircle, Loader
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const TABS = [
  { id: 'acceleration', label: 'Acceleration', icon: Rocket },
  { id: 'deploy', label: 'Deploy', icon: Cloud },
  { id: 'monitor', label: 'Monitor', icon: Activity },
  { id: 'neplit', label: 'Neplit', icon: Package },
  { id: 'games', label: 'Games', icon: Gamepad2 },
  { id: 'clips', label: 'Clips', icon: Video },
  { id: 'mockups', label: 'Mockups', icon: Layout },
  { id: 'proof', label: 'Proof', icon: Image },
  { id: 'community', label: 'Community Wall', icon: Twitter },
  { id: 'livefeed', label: 'Live Feed', icon: Rss },
  { id: 'submissions', label: 'Submissions', icon: UserPlus },
  { id: 'content', label: 'Content', icon: Settings },
  { id: 'comments', label: 'Comments', icon: MessageSquare },
  { id: 'emails', label: 'Emails', icon: Mail },
  { id: 'petition', label: 'Petition', icon: Trophy },
];

// ============ LOGIN ============
function Login({ onLogin }) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_URL}/api/admin/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      });
      if (res.ok) {
        sessionStorage.setItem('adminLoggedIn', 'true');
        onLogin();
      } else {
        setError('Invalid password');
      }
    } catch {
      setError('Connection failed');
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="bg-card-black border border-white/10 rounded-lg p-8 w-full max-w-md">
        <h1 className="font-heading text-3xl text-primary mb-2 text-center">Admin Login</h1>
        <p className="text-white/60 text-center mb-6">NBA 2K Legacy Vault</p>
        <form onSubmit={handleLogin}>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter admin password"
            className="w-full px-4 py-3 bg-black border border-white/20 rounded text-white placeholder-white/40 focus:outline-none focus:border-primary mb-4"
          />
          {error && <p className="text-red-400 text-sm mb-4">{error}</p>}
          <button type="submit" className="w-full py-3 bg-primary hover:bg-primary-hover text-white font-bold rounded transition">
            Login
          </button>
        </form>
      </div>
    </div>
  );
}

// ============ GAMES TAB ============
function GamesTab() {
  const [games, setGames] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);

  useEffect(() => { fetchGames(); }, []);

  const fetchGames = async () => {
    try {
      const res = await fetch(`${API_URL}/api/games/all`);
      const data = await res.json();
      setGames(Array.isArray(data) ? data : []);
    } catch { setGames([]); }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this game?')) return;
    await fetch(`${API_URL}/api/games/${id}`, { method: 'DELETE' });
    fetchGames();
  };

  const handleSave = async (game) => {
    if (editing) {
      await fetch(`${API_URL}/api/games/${editing.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(game),
      });
    } else {
      await fetch(`${API_URL}/api/games`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(game),
      });
    }
    setShowModal(false);
    setEditing(null);
    fetchGames();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="font-heading text-3xl text-white">Manage Games</h2>
        <button onClick={() => { setEditing(null); setShowModal(true); }} className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded transition">
          <Plus size={16} /> Add Game
        </button>
      </div>
      <div className="grid md:grid-cols-2 gap-4">
        {games.map((g) => (
          <div key={g.id} className="bg-card-black border border-white/10 rounded-lg p-4">
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-white font-bold text-lg">{g.title}</h3>
              <span className="text-white/40 text-sm">{g.year}</span>
            </div>
            <p className="text-white/60 text-sm mb-2">{g.hook_text}</p>
            <p className="text-white/40 text-xs mb-3">Order: {g.order}</p>
            <div className="flex gap-2">
              <button onClick={() => { setEditing(g); setShowModal(true); }} className="p-2 hover:bg-white/10 rounded text-white/60 hover:text-white">
                <Edit size={16} />
              </button>
              <button onClick={() => handleDelete(g.id)} className="p-2 hover:bg-white/10 rounded text-red-400 hover:text-red-300">
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>
      {showModal && (
        <GameModal game={editing} onSave={handleSave} onClose={() => { setShowModal(false); setEditing(null); }} />
      )}
    </div>
  );
}

function GameModal({ game, onSave, onClose }) {
  const [form, setForm] = useState(game || { title: '', year: '', hook_text: '', cover_athletes: '', description: '', cover_image: '', order: 0 });
  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
      <div className="bg-card-black border border-white/10 rounded-lg p-6 w-full max-w-lg">
        <h3 className="font-heading text-xl text-white mb-4">{game ? 'Edit Game' : 'Add Game'}</h3>
        <div className="space-y-3">
          <input placeholder="Title (e.g. NBA 2K15)" value={form.title} onChange={(e) => setForm({...form, title: e.target.value})} className="w-full px-3 py-2 bg-black border border-white/20 rounded text-white placeholder-white/40" />
          <input placeholder="Year" value={form.year} onChange={(e) => setForm({...form, year: e.target.value})} className="w-full px-3 py-2 bg-black border border-white/20 rounded text-white placeholder-white/40" />
          <input placeholder="Hook Text" value={form.hook_text} onChange={(e) => setForm({...form, hook_text: e.target.value})} className="w-full px-3 py-2 bg-black border border-white/20 rounded text-white placeholder-white/40" />
          <input placeholder="Cover Athletes" value={form.cover_athletes} onChange={(e) => setForm({...form, cover_athletes: e.target.value})} className="w-full px-3 py-2 bg-black border border-white/20 rounded text-white placeholder-white/40" />
          <input placeholder="Cover Image URL" value={form.cover_image} onChange={(e) => setForm({...form, cover_image: e.target.value})} className="w-full px-3 py-2 bg-black border border-white/20 rounded text-white placeholder-white/40" />
          <textarea placeholder="Description" value={form.description} onChange={(e) => setForm({...form, description: e.target.value})} className="w-full px-3 py-2 bg-black border border-white/20 rounded text-white placeholder-white/40 h-20" />
          <input type="number" placeholder="Order" value={form.order} onChange={(e) => setForm({...form, order: parseInt(e.target.value)})} className="w-full px-3 py-2 bg-black border border-white/20 rounded text-white placeholder-white/40" />
        </div>
        <div className="flex gap-2 mt-4">
          <button onClick={onClose} className="flex-1 py-2 border border-white/20 text-white/70 hover:bg-white/10 rounded">Cancel</button>
          <button onClick={() => onSave(form)} className="flex-1 py-2 bg-primary hover:bg-primary-hover text-white rounded">Save</button>
        </div>
      </div>
    </div>
  );
}

// ============ CLIPS TAB ============
function ClipsTab() {
  const [clips, setClips] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);

  useEffect(() => { fetchClips(); }, []);

  const fetchClips = async () => {
    try {
      const res = await fetch(`${API_URL}/api/clips/all`);
      const data = await res.json();
      setClips(Array.isArray(data) ? data : []);
    } catch { setClips([]); }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this clip?')) return;
    await fetch(`${API_URL}/api/clips/${id}`, { method: 'DELETE' });
    fetchClips();
  };

  const handleSave = async (clip) => {
    if (editing) {
      await fetch(`${API_URL}/api/clips/${editing.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(clip),
      });
    } else {
      await fetch(`${API_URL}/api/clips`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(clip),
      });
    }
    setShowModal(false);
    setEditing(null);
    fetchClips();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="font-heading text-3xl text-white">Manage Clips</h2>
        <button onClick={() => { setEditing(null); setShowModal(true); }} className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded transition">
          <Plus size={16} /> Add Clip
        </button>
      </div>
      <div className="grid md:grid-cols-2 gap-4">
        {clips.map((c) => (
          <div key={c.id} className="bg-card-black border border-white/10 rounded-lg p-4">
            <h3 className="text-white font-bold">{c.title}</h3>
            <p className="text-white/40 text-sm mb-2">{c.platform}</p>
            <a href={c.url} target="_blank" rel="noreferrer" className="text-primary text-sm hover:underline">Watch →</a>
            <div className="flex gap-2 mt-3">
              <button onClick={() => { setEditing(c); setShowModal(true); }} className="p-2 hover:bg-white/10 rounded text-white/60"><Edit size={16} /></button>
              <button onClick={() => handleDelete(c.id)} className="p-2 hover:bg-white/10 rounded text-red-400"><Trash2 size={16} /></button>
            </div>
          </div>
        ))}
      </div>
      {showModal && (
        <ClipModal clip={editing} onSave={handleSave} onClose={() => { setShowModal(false); setEditing(null); }} />
      )}
    </div>
  );
}

function ClipModal({ clip, onSave, onClose }) {
  const [form, setForm] = useState(clip || { title: '', url: '', platform: 'youtube' });
  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
      <div className="bg-card-black border border-white/10 rounded-lg p-6 w-full max-w-lg">
        <h3 className="font-heading text-xl text-white mb-4">{clip ? 'Edit Clip' : 'Add Clip'}</h3>
        <div className="space-y-3">
          <input placeholder="Title" value={form.title} onChange={(e) => setForm({...form, title: e.target.value})} className="w-full px-3 py-2 bg-black border border-white/20 rounded text-white placeholder-white/40" />
          <input placeholder="URL" value={form.url} onChange={(e) => setForm({...form, url: e.target.value})} className="w-full px-3 py-2 bg-black border border-white/20 rounded text-white placeholder-white/40" />
          <select value={form.platform} onChange={(e) => setForm({...form, platform: e.target.value})} className="w-full px-3 py-2 bg-black border border-white/20 rounded text-white">
            <option value="youtube">YouTube</option>
            <option value="tiktok">TikTok</option>
            <option value="twitter">Twitter</option>
          </select>
        </div>
        <div className="flex gap-2 mt-4">
          <button onClick={onClose} className="flex-1 py-2 border border-white/20 text-white/70 hover:bg-white/10 rounded">Cancel</button>
          <button onClick={() => onSave(form)} className="flex-1 py-2 bg-primary hover:bg-primary-hover text-white rounded">Save</button>
        </div>
      </div>
    </div>
  );
}

// ============ SUBSCRIBERS TAB ============
function SubscribersTab() {
  const [subscribers, setSubscribers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchSubscribers(); }, []);

  const fetchSubscribers = async () => {
    try {
      const res = await fetch(`${API_URL}/api/subscribers`, {
        headers: { 'X-Admin-Password': sessionStorage.getItem('adminPassword') || '' }
      });
      if (res.ok) {
        const data = await res.json();
        setSubscribers(Array.isArray(data) ? data : []);
      }
    } catch { setSubscribers([]); }
    setLoading(false);
  };

  const handleDelete = async (id) => {
    await fetch(`${API_URL}/api/subscribers/${id}`, {
      method: 'DELETE',
      headers: { 'X-Admin-Password': sessionStorage.getItem('adminPassword') || '' }
    });
    fetchSubscribers();
  };

  if (loading) return <div className="text-white/60">Loading...</div>;

  return (
    <div className="space-y-6">
      <h2 className="font-heading text-3xl text-white">Email Subscribers ({subscribers.length})</h2>
      <div className="space-y-2">
        {subscribers.map((s) => (
          <div key={s.id} className="bg-card-black border border-white/10 rounded p-4 flex justify-between items-center">
            <div>
              <p className="text-white">{s.email}</p>
              <p className="text-white/40 text-sm">{s.created_at}</p>
            </div>
            <button onClick={() => handleDelete(s.id)} className="p-2 hover:bg-white/10 rounded text-red-400"><Trash2 size={16} /></button>
          </div>
        ))}
        {subscribers.length === 0 && <p className="text-white/40">No subscribers yet.</p>}
      </div>
    </div>
  );
}

// ============ PETITION TAB ============
function PetitionTab() {
  const [count, setCount] = useState(0);
  const [signatures, setSignatures] = useState([]);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => { fetchCount(); }, []);

  const fetchCount = async () => {
    try {
      const res = await fetch(`${API_URL}/api/petition/count`);
      const data = await res.json();
      setCount(data.count || 0);
    } catch {}
  };

  const fetchSignatures = async () => {
    try {
      const res = await fetch(`${API_URL}/api/petition/signatures`);
      const data = await res.json();
      setSignatures(Array.isArray(data) ? data : []);
      setShowAll(true);
    } catch {}
  };

  return (
    <div className="space-y-6">
      <h2 className="font-heading text-3xl text-white">Petition Signatures</h2>
      <div className="bg-card-black border border-primary/50 rounded-lg p-8 text-center">
        <p className="text-6xl font-bold text-primary">{count}</p>
        <p className="text-white/60 mt-2">Total Signatures</p>
      </div>
      {!showAll ? (
        <button onClick={fetchSignatures} className="px-4 py-2 border border-white/20 text-white/70 hover:bg-white/10 rounded">View All Signatures</button>
      ) : (
        <div className="space-y-2">
          {signatures.map((s) => (
            <div key={s.id} className="bg-card-black border border-white/10 rounded p-4">
              <p className="text-white font-medium">{s.name}</p>
              <p className="text-white/40 text-sm">{s.location} {s.handle && `@${s.handle}`}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ============ DEPLOY TAB ============
function DeployTab() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchRuns(); }, []);

  const fetchRuns = async () => {
    try {
      const res = await fetch(`${API_URL}/api/deploy/runs`, {
        headers: { 'X-Admin-Password': sessionStorage.getItem('adminPassword') || '' }
      });
      if (res.ok) {
        const data = await res.json();
        setRuns(Array.isArray(data) ? data : []);
      }
    } catch {}
    setLoading(false);
  };

  if (loading) return <div className="text-white/60">Loading...</div>;

  return (
    <div className="space-y-6">
      <h2 className="font-heading text-3xl text-white">Deploy Live</h2>
      <div className="bg-card-black border border-primary/50 rounded-lg p-6">
        <h3 className="text-white font-bold text-lg mb-2">Deploy this site</h3>
        <p className="text-white/60 text-sm mb-4">GitHub → Atlas → Render → Vercel • One button deploy</p>
        <button disabled className="px-6 py-3 bg-primary/50 text-white/50 rounded cursor-not-allowed">
          Deploy Live (Configure tokens first)
        </button>
      </div>
      <div>
        <h3 className="text-white font-bold mb-4">Deploy History</h3>
        {runs.length === 0 ? (
          <p className="text-white/40">No deploys yet.</p>
        ) : (
          <div className="space-y-2">
            {runs.map((r) => (
              <div key={r.id} className="bg-card-black border border-white/10 rounded p-4">
                <div className="flex justify-between items-center">
                  <span className={`px-2 py-1 rounded text-xs ${r.status === 'success' ? 'bg-green-500/20 text-green-400' : r.status === 'failed' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                    {r.status}
                  </span>
                  <span className="text-white/40 text-sm">{r.created_at}</span>
                </div>
                <p className="text-white/60 text-sm mt-2 font-mono">{r.id}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ============ MONITOR TAB ============
function MonitorTab() {
  const [status, setStatus] = useState({ open_count: 0, status: 'healthy' });
  const [observations, setObservations] = useState([]);

  useEffect(() => { fetchStatus(); fetchObservations(); }, []);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/api/monitor/status`);
      const data = await res.json();
      setStatus(data);
    } catch {}
  };

  const fetchObservations = async () => {
    try {
      const res = await fetch(`${API_URL}/api/monitor/observations`, {
        headers: { 'X-Admin-Password': sessionStorage.getItem('adminPassword') || '' }
      });
      if (res.ok) {
        const data = await res.json();
        setObservations(Array.isArray(data) ? data : []);
      }
    } catch {}
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="font-heading text-3xl text-white">Monitor</h2>
        <div className={`px-4 py-2 rounded-full text-sm font-medium ${status.status === 'healthy' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
          {status.status.toUpperCase()}
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-card-black border border-white/10 rounded-lg p-4 text-center">
          <p className="text-3xl font-bold text-white">{status.open_count}</p>
          <p className="text-white/60 text-sm">Open Issues</p>
        </div>
        <div className="bg-card-black border border-white/10 rounded-lg p-4 text-center">
          <p className="text-3xl font-bold text-green-400">0</p>
          <p className="text-white/60 text-sm">Critical</p>
        </div>
        <div className="bg-card-black border border-white/10 rounded-lg p-4 text-center">
          <p className="text-3xl font-bold text-yellow-400">0</p>
          <p className="text-white/60 text-sm">Warnings</p>
        </div>
      </div>
      <div>
        <h3 className="text-white font-bold mb-4">Observations</h3>
        {observations.length === 0 ? (
          <p className="text-white/40">No observations.</p>
        ) : (
          <div className="space-y-2">
            {observations.map((o) => (
              <div key={o.id} className="bg-card-black border border-white/10 rounded p-4">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${o.severity === 'critical' ? 'bg-red-500' : o.severity === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'}`}></span>
                  <span className="text-white font-medium">{o.title}</span>
                </div>
                <p className="text-white/60 text-sm mt-1">{o.detail}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ============ ACCELERATION TAB ============
function AccelerationTab() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/vault-guide`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Connection failed. Is the backend running?' }]);
    }
    setLoading(false);
  };

  return (
    <div className="space-y-6 h-[600px] flex flex-col">
      <h2 className="font-heading text-3xl text-white flex items-center gap-2">
        <Sparkles className="text-primary" /> Acceleration Agent
      </h2>
      <div className="flex-1 bg-card-black border border-white/10 rounded-lg p-4 overflow-y-auto">
        {messages.length === 0 && (
          <p className="text-white/40">Welcome to the Acceleration Agent. Ask me anything about the site!</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`mb-4 ${m.role === 'user' ? 'text-right' : ''}`}>
            <div className={`inline-block px-4 py-2 rounded-lg ${m.role === 'user' ? 'bg-primary text-white' : 'bg-white/10 text-white/90'}`}>
              {m.content}
            </div>
          </div>
        ))}
        {loading && <div className="text-white/40 animate-pulse">Thinking...</div>}
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask the agent..."
          className="flex-1 px-4 py-3 bg-black border border-white/20 rounded text-white placeholder-white/40 focus:outline-none focus:border-primary"
        />
        <button onClick={handleSend} disabled={loading} className="px-6 py-3 bg-primary hover:bg-primary-hover text-white rounded transition disabled:opacity-50">
          <Send size={20} />
        </button>
      </div>
    </div>
  );
}

// ============ PLACEHOLDER TABS ============
function PlaceholderTab({ name }) {
  return (
    <div className="space-y-6">
      <h2 className="font-heading text-3xl text-white">{name}</h2>
      <div className="bg-card-black border border-white/10 rounded-lg p-8 text-center">
        <p className="text-white/60">{name} management panel</p>
        <p className="text-white/40 text-sm mt-2">Connect to your backend to enable this feature</p>
      </div>
    </div>
  );
}

// ============ MAIN APP ============
function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(sessionStorage.getItem('adminLoggedIn') === 'true');
  const [activeTab, setActiveTab] = useState('games');

  if (!isLoggedIn) return <Login onLogin={() => setIsLoggedIn(true)} />;

  const renderTab = () => {
    switch (activeTab) {
      case 'games': return <GamesTab />;
      case 'clips': return <ClipsTab />;
      case 'emails': return <SubscribersTab />;
      case 'petition': return <PetitionTab />;
      case 'deploy': return <DeployTab />;
      case 'monitor': return <MonitorTab />;
      case 'acceleration': return <AccelerationTab />;
      default: return <PlaceholderTab name={TABS.find(t => t.id === activeTab)?.label || activeTab} />;
    }
  };

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-card-black border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <a href="/" className="text-white/60 hover:text-white text-sm">← Back to Site</a>
          <h1 className="font-heading text-xl text-white">Full Admin Control</h1>
          <div className="flex items-center gap-4">
            <button onClick={() => { sessionStorage.clear(); setIsLoggedIn(false); }} className="text-white/60 hover:text-white text-sm">Logout</button>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="bg-card-black border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 py-2 flex flex-wrap gap-1">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded text-sm font-medium transition ${
                  activeTab === tab.id 
                    ? 'bg-primary text-white' 
                    : 'text-white/60 hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon size={16} />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {renderTab()}
      </main>
    </div>
  );
}

export default App;
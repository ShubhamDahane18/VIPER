import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Activity, Search, ListTodo, Shield, FileAudio, LayoutDashboard } from 'lucide-react';
import DashboardComponent from './components/DashboardComponent';
import SetupComponent from './components/SetupComponent';
import RAGSearchComponent from './components/RAGSearchComponent';
import ApprovalQueueComponent from './components/ApprovalQueueComponent';
import AuditLogsComponent from './components/AuditLogsComponent';
import { setAuthUser } from './api';

function App() {
    const [role, setRole] = React.useState('admin_user');

    React.useEffect(() => {
        setAuthUser(role);
    }, [role]);

    return (
        <Router>
            <div className="flex h-screen bg-viper-900 text-slate-300">
                <aside className="w-64 bg-viper-800 border-r border-slate-700 flex flex-col">
                    <div className="p-6 border-b border-slate-700 flex items-center gap-3">
                        <Shield className="w-8 h-8 text-viper-accent" />
                        <h1 className="text-2xl font-bold tracking-wider text-white">VIPER</h1>
                    </div>

                    <nav className="flex-1 p-4 space-y-2">
                        <Link to="/" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-700 transition">
                            <LayoutDashboard className="w-5 h-5" /> Dashboard
                        </Link>
                        <Link to="/meetings" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-700 transition">
                            <FileAudio className="w-5 h-5" /> Meetings
                        </Link>
                        <Link to="/search" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-700 transition">
                            <Search className="w-5 h-5" /> RAG Search
                        </Link>
                        <Link to="/approvals" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-700 transition">
                            <ListTodo className="w-5 h-5" /> Action Queue
                        </Link>
                        <Link to="/audit" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-700 transition">
                            <Activity className="w-5 h-5" /> Audit Logs
                        </Link>
                    </nav>

                    <div className="p-4 border-t border-slate-700">
                        <label className="text-xs text-slate-400 uppercase tracking-widest mb-2 block">Simulate User Check</label>
                        <select
                            value={role}
                            onChange={(e) => setRole(e.target.value)}
                            className="w-full bg-slate-700 border border-slate-600 rounded p-2 text-sm text-white"
                        >
                            <option value="admin_user">Admin (All Access)</option>
                            <option value="legal_user">Legal (Restricted)</option>
                            <option value="eng_user">Engineering (Restricted)</option>
                            <option value="sales_user">Sales (Restricted)</option>
                        </select>
                    </div>
                </aside>

                <main className="flex-1 overflow-y-auto">
                    <div className="p-8">
                        <Routes>
                            <Route path="/" element={<DashboardComponent />} />
                            <Route path="/meetings" element={<SetupComponent />} />
                            <Route path="/search" element={<RAGSearchComponent activeRole={role} />} />
                            <Route path="/approvals" element={<ApprovalQueueComponent />} />
                            <Route path="/audit" element={<AuditLogsComponent activeRole={role} />} />
                        </Routes>
                    </div>
                </main>
            </div>
        </Router>
    );
}

export default App;

import React, { useState, useEffect } from 'react';
import { getAuditLogs } from '../api';
import { Activity, ShieldAlert } from 'lucide-react';

export default function AuditLogsComponent({ activeRole }: { activeRole: string }) {
    const [logs, setLogs] = useState<any[]>([]);
    const [error, setError] = useState('');

    useEffect(() => {
        if (activeRole !== 'admin_user') {
            setError('Access Denied. Only Admin role can view Audit Logs.');
            setLogs([]);
            return;
        }
        setError('');
        getAuditLogs().then(setLogs).catch(e => setError('Failed to fetch audit logs'));
    }, [activeRole]);

    return (
        <div className="space-y-6 max-w-5xl">
            <div>
                <h2 className="text-3xl font-light text-white mb-2">Immutable Audit Log</h2>
                <p className="text-slate-400">Append-only chronological record of all system access and queries.</p>
            </div>

            {error ? (
                <div className="p-12 text-center bg-red-900/20 border border-red-500/50 rounded-lg flex flex-col items-center gap-4 text-red-400">
                    <ShieldAlert className="w-12 h-12" />
                    <p className="font-bold tracking-widest uppercase">{error}</p>
                </div>
            ) : (
                <div className="bg-viper-800 rounded-lg border border-slate-700 overflow-hidden shadow">
                    <table className="w-full text-left text-sm text-slate-300">
                        <thead className="bg-slate-900/50 text-slate-400 uppercase tracking-wider text-xs">
                            <tr>
                                <th className="px-6 py-4">Timestamp</th>
                                <th className="px-6 py-4">User ID</th>
                                <th className="px-6 py-4">Action</th>
                                <th className="px-6 py-4">Entity</th>
                                <th className="px-6 py-4">Description</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700/50">
                            {logs.map((log) => (
                                <tr key={log.id} className="hover:bg-slate-700/20 transition">
                                    <td className="px-6 py-4 font-mono text-xs">{new Date(log.timestamp).toLocaleString()}</td>
                                    <td className="px-6 py-4">{log.user_id}</td>
                                    <td className="px-6 py-4 font-medium text-emerald-400">{log.action}</td>
                                    <td className="px-6 py-4">{log.entity || '-'}</td>
                                    <td className="px-6 py-4 max-w-xs truncate">{log.description || '-'}</td>
                                </tr>
                            ))}
                            {logs.length === 0 && (
                                <tr>
                                    <td colSpan={5} className="px-6 py-12 text-center text-slate-500">No logs found.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

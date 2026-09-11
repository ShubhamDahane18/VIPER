import React, { useState, useEffect } from 'react';
import { getPendingActions, approveAction, rejectAction } from '../api';
import { Check, X, Calendar, User as UserIcon } from 'lucide-react';

export default function ApprovalQueueComponent() {
    const [tasks, setTasks] = useState<any[]>([]);

    useEffect(() => {
        fetchTasks();
    }, []);

    const fetchTasks = async () => {
        try {
            const data = await getPendingActions();
            setTasks(data);
        } catch (e) {
            console.error(e);
        }
    };

    const handleApprove = async (id: number) => {
        await approveAction(id);
        fetchTasks();
    };

    const handleReject = async (id: number) => {
        await rejectAction(id);
        fetchTasks();
    };

    return (
        <div className="space-y-6 max-w-5xl">
            <div>
                <h2 className="text-3xl font-light text-white mb-2">Human-in-the-Loop Approval</h2>
                <p className="text-slate-400">Review LangGraph extracted action items before they are synced to CRM/Email systems.</p>
            </div>

            <div className="grid gap-4">
                {tasks.length === 0 ? (
                    <div className="p-8 text-center text-slate-500 bg-viper-800 rounded-lg border border-slate-700">
                        No pending actions requiring approval.
                    </div>
                ) : (
                    tasks.map(t => (
                        <div key={t.id} className="flex flex-col md:flex-row md:items-center justify-between p-5 bg-viper-800 border border-slate-700 rounded-lg hover:border-slate-500 transition shadow-lg">
                            <div className="space-y-2 mb-4 md:mb-0">
                                <div className="text-lg font-medium text-white">{t.task_description}</div>
                                <div className="flex gap-4 text-sm text-slate-400">
                                    <span className="flex items-center gap-1"><UserIcon className="w-4 h-4" /> Owner: {t.owner || 'Unknown'}</span>
                                    <span className="flex items-center gap-1"><Calendar className="w-4 h-4" /> Deadline: {t.deadline || 'None'}</span>
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <button onClick={() => handleApprove(t.id)} className="bg-emerald-500 hover:bg-emerald-400 text-white px-4 py-2 rounded font-medium flex items-center gap-2 transition">
                                    <Check className="w-4 h-4" /> Approve Sync
                                </button>
                                <button onClick={() => handleReject(t.id)} className="bg-slate-700 hover:bg-red-500 text-white px-4 py-2 rounded font-medium flex items-center gap-2 transition">
                                    <X className="w-4 h-4" /> Reject
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

import React, { useEffect, useState } from 'react';
import { getMeetings } from '../api';
import { Server, Mic } from 'lucide-react';

export default function DashboardComponent() {
    const [meetings, setMeetings] = useState<any[]>([]);

    useEffect(() => {
        getMeetings().then(setMeetings).catch(console.error);
    }, []);

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-3xl font-light text-white mb-2">System Overview</h2>
                <p className="text-slate-400">Air-gapped on-premises environment status.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-6 bg-viper-800 rounded-lg border border-slate-700 shadow flex items-start gap-4">
                    <div className="p-3 bg-emerald-900/30 text-emerald-400 rounded-lg"><Server className="w-6 h-6" /></div>
                    <div>
                        <div className="text-2xl font-bold text-white">Online</div>
                        <div className="text-sm text-slate-400">Inference APIs (Local)</div>
                    </div>
                </div>
                <div className="p-6 bg-viper-800 rounded-lg border border-slate-700 shadow flex items-start gap-4">
                    <div className="p-3 bg-blue-900/30 text-blue-400 rounded-lg"><Mic className="w-6 h-6" /></div>
                    <div>
                        <div className="text-2xl font-bold text-white">{meetings.length}</div>
                        <div className="text-sm text-slate-400">Meetings Indexed</div>
                    </div>
                </div>
                <div className="p-6 bg-viper-800 rounded-lg border border-slate-700 shadow">
                    <div className="text-sm font-bold tracking-widest uppercase text-slate-500 mb-2">Storage Policy</div>
                    <div className="text-slate-300 text-sm space-y-1">
                        <div className="flex justify-between"><span>Vector DB:</span> <span className="text-white">Qdrant Local</span></div>
                        <div className="flex justify-between"><span>Audio Store:</span> <span className="text-white">Local FS</span></div>
                        <div className="flex justify-between"><span>Relational:</span> <span className="text-white">SQLite MVP</span></div>
                    </div>
                </div>
            </div>

            <div className="bg-viper-800 p-6 rounded-lg border border-slate-700 shadow">
                <h3 className="text-xl font-bold text-white mb-4">Architecture Simulation Notice</h3>
                <p className="text-slate-300 text-sm leading-relaxed max-w-3xl">
                    This is a prototype simulating Project VIPER's architecture. Transcripts are sent to a local LLM API for RAG responses.
                    Use the Python Device Simulator to ingest new audio. Accessing RAG with the wrong simulator role will trigger local ACL filtering, demonstrating the security boundaries.
                </p>
            </div>
        </div>
    );
}

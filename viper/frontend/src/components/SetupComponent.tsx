import React, { useState, useEffect } from 'react';
import { getMeetings } from '../api';
import { PlayCircle, ShieldCheck } from 'lucide-react';

export default function SetupComponent() {
    const [meetings, setMeetings] = useState<any[]>([]);

    useEffect(() => {
        fetchMeetings();
    }, []);

    const fetchMeetings = async () => {
        try {
            const data = await getMeetings();
            setMeetings(data);
        } catch (e) {
            console.error("error fetching meetings");
        }
    };

    return (
        <div className="space-y-6 max-w-5xl">
            <div>
                <h2 className="text-3xl font-light text-white mb-2">Ingested Meetings</h2>
                <p className="text-slate-400">View redacted transcripts. Access controlled via RBAC.</p>
            </div>

            <div className="grid gap-4">
                {meetings.length === 0 ? (
                    <div className="p-8 text-center text-slate-500 bg-viper-800 rounded-lg border border-slate-700">
                        No meetings indexed or you lack access to view any. Use the Python script to simulate H-R191 file transfer.
                    </div>
                ) : (
                    meetings.map(m => (
                        <div key={m.id} className="flex flex-col md:flex-row md:items-center justify-between p-6 bg-viper-800 border border-slate-700 rounded-lg shadow-lg">
                            <div className="space-y-1">
                                <div className="text-xl font-medium text-white flex items-center gap-2">
                                    <PlayCircle className="w-5 h-5 text-slate-400" /> {m.title}
                                </div>
                                <div className="text-sm text-slate-400 font-mono">
                                    Device: {m.device_serial} • Initiated: {new Date(m.startTime).toLocaleString()}
                                </div>
                                <div className="flex gap-2 items-center mt-3 pt-3 border-t border-slate-700/50">
                                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                                    <span className="text-xs uppercase tracking-widest text-slate-400">Allowed Roles: {m.allowed_roles}</span>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

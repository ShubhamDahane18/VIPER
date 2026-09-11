import React, { useState, useEffect } from 'react';
import { searchRAG } from '../api';
import { Search, Loader2, AlertCircle } from 'lucide-react';

export default function RAGSearchComponent({ activeRole }: { activeRole: string }) {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Clear results if user swaps role to demonstrate ACL
    useEffect(() => {
        setResults(null);
    }, [activeRole]);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        setError('');

        try {
            const data = await searchRAG(query);
            setResults(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Error communicating with server');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6 max-w-4xl">
            <div>
                <h2 className="text-3xl font-light text-white mb-2">Knowledge Retrieval</h2>
                <p className="text-slate-400">Search across past meetings. Results are strictly filtered by your current ACL role: <span className="text-viper-accent font-semibold">{activeRole}</span></p>
            </div>

            <form onSubmit={handleSearch} className="flex gap-4">
                <input
                    type="text"
                    className="flex-1 bg-viper-800 border-slate-600 rounded-lg p-4 text-white focus:ring-2 focus:ring-viper-accent outline-none"
                    placeholder="e.g. What was the budget decision for Project X?"
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                />
                <button
                    disabled={loading}
                    type="submit"
                    className="bg-viper-accent hover:bg-emerald-400 text-white font-bold py-4 px-8 rounded-lg flex items-center gap-2 transition disabled:opacity-50"
                >
                    {loading ? <Loader2 className="animate-spin w-5 h-5" /> : <Search className="w-5 h-5" />}
                    Query
                </button>
            </form>

            {error && (
                <div className="p-4 bg-red-900/30 border border-red-500 rounded flex gap-3 text-red-400">
                    <AlertCircle />
                    {error}
                </div>
            )}

            {results && (
                <div className="space-y-6">
                    <div className="p-6 bg-viper-800 rounded-lg border border-slate-700 shadow-xl">
                        <h3 className="text-sm font-bold tracking-widest text-slate-400 uppercase mb-4">Synthesized Answer</h3>
                        <p className="text-lg leading-relaxed text-slate-200">
                            {results.answer}
                        </p>
                    </div>

                    <div className="space-y-3">
                        <h3 className="text-sm font-bold tracking-widest text-slate-400 uppercase">Cryptographic Citations</h3>
                        {results.citations.length === 0 ? (
                            <p className="text-slate-500 italic">No citations available.</p>
                        ) : (
                            results.citations.map((cite: string, idx: number) => (
                                <div key={idx} className="p-3 bg-slate-800 rounded border border-slate-700 text-sm font-mono text-emerald-400/80 break-all">
                                    {cite}
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

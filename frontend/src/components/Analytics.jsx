import React, { useState, useEffect } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts';
import { Activity, Database, Calendar } from 'lucide-react';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const Analytics = () => {
    const [summary, setSummary] = useState(null);
    const [timeline, setTimeline] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000); // Poll every 5s
        return () => clearInterval(interval);
    }, []);

    const fetchData = async () => {
        try {
            const [summaryRes, timelineRes] = await Promise.all([
                fetch('http://localhost:8000/ analytics/summary'), // Space intentional to fix later or just fix now? Fix now. 
                fetch('http://localhost:8000/analytics/timeline')
            ]);

            // Correction for URL
            // fetch('http://localhost:8000/analytics/summary')

            if (summaryRes.ok && timelineRes.ok) {
                const summaryData = await summaryRes.json();
                const timelineData = await timelineRes.json();

                setSummary(summaryData);
                setTimeline(timelineData);
            }
        } catch (error) {
            console.error("Failed to fetch analytics", error);
        } finally {
            setLoading(false);
        }
    };

    // Fix the fetch URL in actual code
    const safeFetchData = async () => {
        try {
            const summaryRes = await fetch('http://localhost:8000/analytics/summary');
            const timelineRes = await fetch('http://localhost:8000/analytics/timeline');

            const summaryData = await summaryRes.json();
            const timelineData = await timelineRes.json();

            setSummary(summaryData);
            setTimeline(timelineData);
        } catch (error) {
            console.error("Failed to fetch analytics", error);
        } finally {
            setLoading(false);
        }
    }

    // Use safeFetchData in useEffect
    useEffect(() => {
        safeFetchData();
        const interval = setInterval(safeFetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="pt-24 text-center text-slate-400">Loading analytics...</div>;

    return (
        <div className="pt-24 pb-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold text-white mb-8">Analytics Dashboard</h1>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="glass-panel p-6 flex items-center gap-4">
                    <div className="p-3 rounded-lg bg-blue-500/20 text-blue-400">
                        <Database className="w-6 h-6" />
                    </div>
                    <div>
                        <p className="text-sm text-slate-400">Total Waste Detected</p>
                        <h3 className="text-2xl font-bold text-white">{summary?.total_events || 0}</h3>
                    </div>
                </div>

                <div className="glass-panel p-6 flex items-center gap-4">
                    <div className="p-3 rounded-lg bg-green-500/20 text-green-400">
                        <Activity className="w-6 h-6" />
                    </div>
                    <div>
                        <p className="text-sm text-slate-400">Most Common Waste</p>
                        <h3 className="text-2xl font-bold text-white">
                            {summary?.distribution?.[0]?.name || "N/A"}
                        </h3>
                    </div>
                </div>

                <div className="glass-panel p-6 flex items-center gap-4">
                    <div className="p-3 rounded-lg bg-purple-500/20 text-purple-400">
                        <Calendar className="w-6 h-6" />
                    </div>
                    <div>
                        <p className="text-sm text-slate-400">Data Range</p>
                        <h3 className="text-2xl font-bold text-white">Last 7 Days</h3>
                    </div>
                </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Composition Chart */}
                <div className="glass-panel p-6">
                    <h3 className="text-lg font-bold text-white mb-6">Waste Composition</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={summary?.distribution || []}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {(summary?.distribution || []).map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Timeline Chart */}
                <div className="glass-panel p-6">
                    <h3 className="text-lg font-bold text-white mb-6">Detection Timeline</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={timeline}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="date" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                                    cursor={{ fill: '#334155', opacity: 0.2 }}
                                />
                                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Analytics;

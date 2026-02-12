import React, { useState, useEffect } from 'react';
import {
    Play,
    Square,
    Activity,
    Box,
    AlertTriangle,
    RefreshCw,
    Camera,
    Wallet,
    Plus
} from 'lucide-react';
import { useWeb3 } from '../context/Web3Context';

const StatCard = ({ icon: Icon, label, value, color }) => (
    <div className="glass-panel p-6 flex items-center justify-between">
        <div>
            <p className="text-slate-400 text-sm font-medium mb-1">{label}</p>
            <h3 className="text-2xl font-bold text-white">{value}</h3>
        </div>
        <div className={`w-12 h-12 rounded-lg ${color} bg-opacity-10 flex items-center justify-center`}>
            <Icon className={`w-6 h-6 ${color.replace('bg-', 'text-')}`} />
        </div>
    </div>
);

const Dashboard = () => {
    const { currentAccount, connectWallet, createWaste } = useWeb3();
    const [isPlaying, setIsPlaying] = useState(false);
    const [stats, setStats] = useState({
        fps: 0,
        detections: 0,
        events: 0,
        frames: 0
    });
    const [mode, setMode] = useState('Initializing...');
    const [logs, setLogs] = useState([]);
    const [autoLog, setAutoLog] = useState(false);

    useEffect(() => {
        // Poll stats every second
        const interval = setInterval(fetchStats, 1000);

        // WebSocket connection for real-time events
        const ws = new WebSocket('ws://localhost:8000/ws/notifications');

        ws.onopen = () => console.log('Connected to WebSocket');

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'event' && data.events) {
                    // Handle new events
                    const newEvents = data.events.map(e => ({
                        ...e,
                        timestamp: new Date().toISOString()
                    }));

                    setLogs(prev => [...newEvents, ...prev].slice(0, 50));

                    // Trigger Auto-Log if enabled
                    if (autoLog) {
                        newEvents.forEach(e => {
                            if (e.event_type === 'waste_detected' || e.event_type === 'waste_classified') {
                                // Extract class name or default
                                const wasteType = e.class_name || "Unknown Waste";
                                handleAutoCreateWaste(wasteType);
                            }
                        });
                    }
                }
            } catch (err) {
                console.error("WS Message Error", err);
            }
        };

        return () => {
            clearInterval(interval);
            ws.close();
        };
    }, [autoLog, currentAccount]); // Re-run if autoLog/account changes

    const fetchStats = async () => {
        try {
            const res = await fetch('http://localhost:8000/video/stats');
            const data = await res.json();
            setStats({
                fps: Math.round(data.avg_fps || 0),
                detections: data.detections_count || 0,
                events: data.events_count || 0,
                frames: data.frames_processed || 0
            });
        } catch (err) {
            console.error("Failed to fetch stats", err);
        }
    };

    const handleStart = async () => {
        try {
            const res = await fetch('http://localhost:8000/video/start', { method: 'POST' });
            const data = await res.json();
            if (data.status === 'started' || data.status === 'already_running') {
                setIsPlaying(true);
                setMode(data.mode === 'synthetic' ? 'Synthetic Demo' : 'Live Camera');
            }
        } catch (err) {
            console.error("Failed to start video", err);
        }
    };

    const handleStop = async () => {
        try {
            await fetch('http://localhost:8000/video/stop', { method: 'POST' });
            setIsPlaying(false);
        } catch (err) {
            console.error("Failed to stop video", err);
        }
    };

    const handleCreateMockWaste = async () => {
        if (!currentAccount) return;
        try {
            await createWaste("Plastic Bottle");
            alert("Waste created on Blockchain!");
        } catch (error) {
            console.error("Error creating waste", error);
            alert("Error creating waste");
        }
    };

    const handleAutoCreateWaste = async (wasteType) => {
        if (!currentAccount) return;
        try {
            console.log(`Auto-logging waste: ${wasteType}`);
            await createWaste(wasteType);
            // Optionally add a toast here
        } catch (error) {
            console.error("Auto-log error:", error);
        }
    };

    return (
        <div className="pt-24 pb-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="mb-8 flex flex-col md:flex-row items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Live Monitor</h1>
                    <p className="text-slate-400 flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${isPlaying ? 'bg-green-500 animate-pulse' : 'bg-slate-500'}`}></span>
                        System Status: {isPlaying ? 'Active' : 'Standby'}
                        <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 ml-2">{mode}</span>
                    </p>
                </div>

                <div className="flex gap-4">
                    {!currentAccount ? (
                        <button
                            onClick={connectWallet}
                            className="px-6 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-medium flex items-center gap-2 transition-colors"
                        >
                            <Wallet className="w-4 h-4" /> Connect Wallet
                        </button>
                    ) : (
                        <div className="flex gap-2">
                            <div className="px-4 py-2 rounded-lg bg-white/10 text-white font-mono text-sm flex items-center">
                                {currentAccount.slice(0, 6)}...{currentAccount.slice(-4)}
                            </div>
                            <button
                                onClick={handleCreateMockWaste}
                                className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-medium flex items-center gap-2 transition-colors"
                            >
                                <Plus className="w-4 h-4" /> Mock Data
                            </button>
                        </div>
                    )}

                    {!isPlaying ? (
                        <button
                            onClick={handleStart}
                            className="px-6 py-2 rounded-lg bg-green-600 hover:bg-green-700 text-white font-medium flex items-center gap-2 transition-colors"
                        >
                            <Play className="w-4 h-4" /> Start Feed
                        </button>
                    ) : (
                        <button
                            onClick={handleStop}
                            className="px-6 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white font-medium flex items-center gap-2 transition-colors"
                        >
                            <Square className="w-4 h-4" /> Stop Feed
                        </button>
                    )}
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <StatCard
                    icon={Activity}
                    label="Processing FPS"
                    value={stats.fps}
                    color="bg-blue-500"
                />
                <StatCard
                    icon={Box}
                    label="Total Detections"
                    value={stats.detections}
                    color="bg-purple-500"
                />
                <StatCard
                    icon={AlertTriangle}
                    label="Events Detected"
                    value={stats.events}
                    color="bg-orange-500"
                />
                <StatCard
                    icon={Camera}
                    label="Frames Processed"
                    value={stats.frames}
                    color="bg-emerald-500"
                />
            </div>

            {/* Main Content Area */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Video Feed */}
                <div className="lg:col-span-2 glass-panel p-1 rounded-2xl overflow-hidden aspect-video relative bg-black">
                    {isPlaying ? (
                        <img
                            src="http://localhost:8000/video/feed"
                            alt="Live Feed"
                            className="w-full h-full object-contain"
                        />
                    ) : (
                        <div className="absolute inset-0 flex items-center justify-center flex-col text-slate-500">
                            <Camera className="w-16 h-16 mb-4 opacity-50" />
                            <p>Feed Stopped</p>
                        </div>
                    )}
                </div>

                {/* Recent Logs / Activity */}
                <div className="glass-panel p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="font-bold text-white">Activity Log</h3>
                        <button className="text-slate-400 hover:text-white">
                            <RefreshCw className="w-4 h-4" />
                        </button>
                    </div>
                    <div className="space-y-4">
                        {logs.length === 0 ? (
                            <p className="text-slate-500 text-center py-4">No recent activity</p>
                        ) : (
                            logs.map((log, i) => (
                                <div key={i} className="flex items-start gap-3 text-sm p-3 rounded-lg bg-white/5 animate-fade-in">
                                    <div className={`w-2 h-2 mt-1.5 rounded-full ${log.event_type === 'waste_detected' ? 'bg-red-500' : 'bg-primary-500'}`}></div>
                                    <div>
                                        <p className="text-slate-300">
                                            {log.event_type === 'waste_detected' ? `Detected ${log.class_name}` :
                                                log.event_type === 'waste_classified' ? `Classified as ${log.class_name}` :
                                                    log.event_type}
                                        </p>
                                        <p className="text-slate-500 text-xs">
                                            {new Date(log.timestamp).toLocaleTimeString()}
                                        </p>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;

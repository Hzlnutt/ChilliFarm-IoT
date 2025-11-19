// src/App.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; 

const FLASK_IP = "192.168.137.1"; 
const API_URL = `http://192.168.137.1:5000/api/data/latest`;
const REFRESH_INTERVAL = 5000; // 5 detik

// --- Komponen Kartu Sensor ---
const SensorCard = ({ title, value, unit, status = null }) => {
    const displayValue = value !== undefined && value !== null ? value.toFixed(2) : '--';
    return (
        <div className="sensor-card">
            <h3>{title}</h3>
            <p className="value">{displayValue} {unit}</p>
            {status && <p className={`status ${status.toLowerCase().replace(' ', '-')}`}>{status}</p>}
        </div>
    );
};

// --- Komponen Utama Dashboard ---
function Dashboard() {
    const [sensorData, setSensorData] = useState(null);
    const [pumpStatus, setPumpStatus] = useState('OFF');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Fungsi untuk mengambil data sensor terbaru
    const fetchSensorData = async () => {
        try {
            console.log("Fetching from:", API_URL);
            const response = await axios.get(API_URL);
            console.log("Response data:", response.data);
            const data = response.data;
            setSensorData(data);
            
            // Logika sederhana untuk status pompa dari Soil Moisture (simulasi)
            const soilMoisture = data.soil_moisture || 0;
            const isDry = soilMoisture < 40;
            setPumpStatus(isDry ? 'OFF' : 'ON');
            
            setLoading(false);
            setError(null);
        } catch (err) {
            console.error("Gagal mengambil data dari Flask:", err);
            console.error("Error details:", err.response?.status, err.response?.data);
            setError(`Gagal terhubung ke API Flask.\nIP: ${FLASK_IP}\nError: ${err.message}`);
            setLoading(false);
        }
    };

    // Fungsi untuk mengontrol Pompa
    const handleControlPump = async (command) => {
        try {
            setPumpStatus(command === 'on' ? 'WAITING...' : 'WAITING...');
            
            const response = await axios.post(`http://192.168.137.1:5000/api/control`, {
                pump: command
            });

            if (response.status === 200) {
                setPumpStatus(command.toUpperCase());
                alert(`Pompa berhasil diubah menjadi: ${command.toUpperCase()}`);
            } else {
                 setPumpStatus(command === 'on' ? 'OFF' : 'ON'); // Kembalikan status jika gagal
                 alert(`Gagal mengirim perintah. Status: ${response.status}`);
            }
        } catch (err) {
            console.error("Gagal mengirim perintah kontrol:", err);
            setPumpStatus(pumpStatus === 'ON' ? 'OFF' : 'ON'); // Kembalikan status jika gagal
            alert("Error: Gagal terhubung untuk kontrol pompa.");
        }
    };


    // useEffect untuk fetching data secara periodik
    useEffect(() => {
        fetchSensorData(); 
        const intervalId = setInterval(fetchSensorData, REFRESH_INTERVAL);

        // Cleanup function
        return () => clearInterval(intervalId);
    }, []); 

    // Tampilan Loading dan Error
    if (loading) return <div className="loading">Memuat data sensor...</div>;
    if (error) return <div className="error">{error}</div>;
    if (!sensorData) return <div className="loading">Tidak ada data sensor yang diterima.</div>;
    
    // Logika Status Tanah
    const soilMoistureValue = sensorData.soil_moisture || 0;
    const soilStatus = soilMoistureValue < 40 ? 'Kering' : 'Lembab';

    return (
        <div className="dashboard-container">
            <h1>🌿 Chili Garden IoT Dashboard</h1>
            <p className="last-update">
                Terakhir Diperbarui: {new Date(sensorData.timestamp).toLocaleTimeString()}
            </p>

            <hr/>

            <h2>🌡️ Data Sensor Lingkungan</h2>
            <div className="sensor-grid">
                <SensorCard 
                    title="Suhu Udara" 
                    value={sensorData.temperature_c} 
                    unit="°C" 
                />
                <SensorCard 
                    title="Kelembapan Udara" 
                    value={sensorData.humidity_pct} 
                    unit="%" 
                />
                <SensorCard 
                    title="Intensitas Cahaya" 
                    value={sensorData.light_lux} 
                    unit="lux" 
                />
                <SensorCard 
                    title="pH Air" 
                    value={sensorData.ph} 
                    unit="pH" 
                />
            </div>
            
            <hr/>

            <h2>💧 Status Irigasi & Aktuator</h2>
            <div className="actuator-panel">
                <SensorCard 
                    title="Kelembapan Tanah" 
                    value={soilMoistureValue} 
                    unit="%" 
                    status={soilStatus}
                />
                
                <div className="pump-control">
                    <h3>Pompa Air (Manual Control)</h3>
                    <p className={`pump-status ${pumpStatus.toLowerCase()}`}>Status: {pumpStatus}</p>
                    
                    <div className="control-buttons">
                        <button 
                            className="btn-on" 
                            onClick={() => handleControlPump('on')}
                            disabled={pumpStatus === 'ON' || pumpStatus === 'WAITING...'}
                        >
                            NYALA
                        </button>
                        <button 
                            className="btn-off" 
                            onClick={() => handleControlPump('off')}
                            disabled={pumpStatus === 'OFF' || pumpStatus === 'WAITING...'}
                        >
                            MATI
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
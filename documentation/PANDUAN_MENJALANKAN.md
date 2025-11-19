# 🚀 Panduan Menjalankan Project IoT Chili Garden

**Tanggal**: November 18, 2025  
**Status**: ✅ Siap Dijalankan

---

## 📋 Daftar Periksa Persiapan

Sebelum memulai, pastikan Anda memiliki:
- [ ] MQTT Broker (Mosquitto) terinstal
- [ ] Python 3.8+ dengan pip
- [ ] ESP32 dengan MicroPython
- [ ] Kabel USB untuk ESP32
- [ ] WiFi hotspot aktif

---

## 🔧 Langkah 1: Verifikasi IP Hotspot (30 detik)

Buka PowerShell/Command Prompt dan jalankan:

```bash
ipconfig
```

Cari **IPv4 Address dari adapter WiFi hotspot Anda** - contohnya `192.168.137.1`. **Catat IP ini**, karena ini adalah IP hotspot untuk akses cross-device.

---

## 📝 Langkah 2: Update Konfigurasi MQTT (1 menit)

### Edit File: `esp32_garden_mqtt.py`

Buka file `esp32_garden_mqtt.py` dan cari baris:

```python
MQTT_BROKER = "192.168.137.1"
```

**Jika IP hotspot Anda berbeda**, ubah ke IP Address Anda:

```python
MQTT_BROKER = "YOUR_HOTSPOT_IP"  # Ganti dengan IP hotspot Anda dari ipconfig
```

### Edit File: `backend/config.py`

Buka file `backend/config.py` dan pastikan:

```python
MQTT_BROKER = os.environ.get('MQTT_BROKER', '192.168.137.1')
```

Jika IP hotspot Anda berbeda, ubah default value:

```python
MQTT_BROKER = os.environ.get('MQTT_BROKER', 'YOUR_HOTSPOT_IP')
```

### Verifikasi WiFi Credentials

Di `esp32_garden_mqtt.py`, pastikan WiFi SSID dan password sesuai:

```python
WIFI_SSID = "hotspotkeren"   # Ganti dengan SSID hotspot Anda
WIFI_PASS = "87654321"       # Ganti dengan password hotspot Anda
```

---

## 🟢 Langkah 3: Mulai MQTT Broker (30 detik)

Buka **Terminal/PowerShell Baru** dan jalankan:

```bash
mosquitto -p 1883
```

**Output yang diharapkan:**
```
xxxx: Listening on port 1883.
xxxx: IPv6 socket support not available.
```

✅ **MQTT Broker sudah berjalan! Jangan tutup terminal ini.**

---

## 🐍 Langkah 4: Mulai Flask Backend (30 detik)

Buka **Terminal/PowerShell Baru** kedua dan jalankan:

```bash
cd "c:\Users\Acer Nitro 5\Documents\TUGAS SMK TELKOM\TUGAS KELAS XII\project IoT UKL\backend"
python app.py
```

**Output yang diharapkan:**
```
[OK] MQTT connected to 192.168.137.1:1883
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.137.1:5000
```

✅ **Backend sudah berjalan! Jangan tutup terminal ini.**

---

## ✅ Langkah 5: Verifikasi Backend Berfungsi (1 menit)

Buka **Terminal/PowerShell Baru** ketiga dan jalankan:

```bash
curl http://192.168.137.1:5000/api/health
```

**Output yang diharapkan:**
```json
{
  "status": "ok",
  "mqtt": "connected",
  "broker": "192.168.137.1",
  "port": 1883,
  "timestamp": "2025-11-18T10:30:45"
}
```

✅ Backend terhubung dengan MQTT! Lanjut ke langkah berikutnya.

---

## 📤 Langkah 6: Upload Code ke ESP32 (2 menit)

### Opsi A: Menggunakan Thonny IDE (Rekomendasi)

1. **Install Thonny**
   ```bash
   pip install thonny
   ```

2. **Buka Thonny** dari Start Menu

3. **Connect ESP32** via USB ke laptop

4. **Setup MicroPython**
   - Tools → Options → Interpreter
   - Pilih "MicroPython (ESP32)"
   - Port: COM3 (atau port yang terdeteksi)
   - Click OK

5. **Upload File**
   - File → Open
   - Pilih `esp32_garden_mqtt.py`
   - F5 untuk menjalankan

6. **Monitor Output**
   - Lihat Shell panel di bawah untuk melihat:
   ```
   Connecting to WiFi...
   WiFi status: (IP, ...)
   Connected to MQTT broker, subscribed to b'esp32/chili/cmd'
   Sensors: {...}
   ```

### Opsi B: Menggunakan VS Code + PyMakr

1. Install extension "PyMakr" di VS Code
2. Connect ESP32
3. Upload project folder
4. Monitor console output

---

## 🔄 Langkah 7: Verifikasi Data Mengalir (2 menit)

Kembali ke **Terminal/PowerShell ketiga** dan jalankan:

```bash
curl http://192.168.137.1:5000/api/data/latest
```

**Output yang diharapkan:**
```json
{
  "temperature_c": 28.5,
  "humidity_pct": 65.2,
  "soil_moisture": 55,
  "ph": 6.8,
  "light_lux": 1250.0,
  "timestamp": "2025-11-18 10:30:45"
}
```

✅ **Data mengalir dengan sempurna!** System sudah berjalan penuh.

---

## 🎮 Langkah 8: Test Actuator (Optional) (1 menit)

### Test Pompa

```bash
curl -X POST http://192.168.137.1:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"pump": "on"}'
```

**Lihat Console ESP32:** "Pump ON"

### Matikan Pompa

```bash
curl -X POST http://192.168.137.1:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"pump": "off"}'
```

**Lihat Console ESP32:** "Pump OFF"

---

## 📊 Langkah 9: Cek Semua Sensor (1 menit)

```bash
curl http://192.168.137.1:5000/api/sensors
```

**Output yang diharapkan:**
```json
[
  {"id": 1, "name": "DHT22_TEMP", "location": "Chili Plant"},
  {"id": 2, "name": "DHT22_HUMIDITY", "location": "Chili Plant"},
  {"id": 3, "name": "SOIL_MOISTURE", "location": "Chili Plant"},
  {"id": 4, "name": "PH_SENSOR", "location": "Chili Plant"},
  {"id": 5, "name": "BH1750", "location": "Chili Plant"}
]
```

✅ Semua 5 sensor terdaftar!

---

## 📈 Langkah 10: Cek Data Historis (1 menit)

```bash
curl http://192.168.137.1:5000/api/measurements?limit=10
```

**Output:**
```json
[
  {
    "id": 1,
    "sensor_id": 1,
    "sensor_name": "DHT22_TEMP",
    "value": 28.5,
    "unit": "C",
    "timestamp": "2025-11-18 10:30:45"
  },
  ...
]
```

✅ Data historis tersimpan di database!

---

## 🎯 Indikator Kesuksesan

Jika semua yang berikut terpenuhi, system sudah berjalan dengan sempurna:

- ✅ MQTT Broker menunjukkan "Listening on port 1883"
- ✅ Backend menunjukkan "[OK] MQTT connected"
- ✅ ESP32 menunjukkan "Connected to MQTT broker"
- ✅ `/api/health` mengembalikan status "ok"
- ✅ `/api/data/latest` menampilkan pembacaan sensor terkini
- ✅ `/api/sensors` menampilkan 5 sensor
- ✅ Pompa merespons perintah `/api/control`

---

## 🆘 Troubleshooting

### ❌ Masalah: "Connection refused" (MQTT)

**Penyebab**: MQTT broker tidak berjalan atau IP salah

**Solusi**:
1. Pastikan Mosquitto sedang berjalan: `netstat -an | findstr 1883`
2. Verifikasi IP: `ipconfig` → catat IPv4 Address yang benar
3. Update semua file dengan IP yang benar

### ❌ Masalah: Backend tidak connect ke MQTT

**Penyebab**: MQTT broker tidak aktif atau konfigurasi IP salah

**Solusi**:
1. Buka terminal pertama (MQTT) - pastikan masih berjalan
2. Restart backend: `python app.py`
3. Check output: harus menunjukkan "[OK] MQTT connected"

### ❌ Masalah: ESP32 tidak connect ke WiFi

**Penyebab**: SSID atau password WiFi salah

**Solusi**:
1. Buka `esp32_garden_mqtt.py`
2. Verifikasi SSID dan password:
   ```python
   WIFI_SSID = "hotspotkeren"
   WIFI_PASS = "87654321"
   ```
3. Upload ulang ke ESP32

### ❌ Masalah: Data tidak muncul di `/api/data/latest`

**Penyebab**: ESP32 tidak connect atau data tidak dikirim

**Solusi**:
1. Cek console ESP32 untuk error messages
2. Verifikasi MQTT broker berjalan
3. Cek IP address di semua file
4. Test dengan data mock:
   ```bash
   mosquitto_pub -h 192.168.137.1 -p 1883 \
     -t "esp32/chili/data" \
     -m '{"temperature_c": 28.5, "humidity_pct": 65.0, "soil_moisture": 55, "ph": 6.8, "light_lux": 1250.0}'
   ```

### ❌ Masalah: Pompa tidak merespons

**Penyebab**: GPIO 26 tidak terhubung atau relay bermasalah

**Solusi**:
1. Verifikasi wiring: GPIO 26 → Relay coil
2. Pastikan relay memiliki daya eksternal
3. Test relay secara manual dengan multimeter

---

## 📱 Quick Reference API

| Endpoint | Method | Fungsi |
|----------|--------|--------|
| `/api/health` | GET | Status sistem |
| `/api/sensors` | GET | Daftar semua sensor |
| `/api/data/latest` | GET | Pembacaan terkini semua sensor |
| `/api/data/average?hours=1` | GET | Rata-rata per jam |
| `/api/measurements?limit=10` | GET | Data historis (10 terbaru) |
| `/api/control` | POST | Kontrol pompa/servo |

---

## 🔌 Pinout Referensi

```
GPIO 15  → DHT22 DATA (Temp/Humidity)
GPIO 35  → pH Sensor ADC
GPIO 34  → Soil Moisture ADC
GPIO 21  → BH1750 SDA (I2C)
GPIO 22  → BH1750 SCL (I2C)
GPIO 26  → Pump Relay
GPIO 27  → Servo PWM
GND      → Semua sensor & relay
```

---

## 📂 Struktur Folder Project

```
project IoT UKL/
├── documentation/          ← Folder untuk semua dokumentasi
│   ├── PANDUAN_MENJALANKAN.md
│   ├── API_REFERENCE.md
│   └── TROUBLESHOOTING.md
├── backend/                ← Flask API server
│   ├── app.py             (Run: python app.py)
│   ├── config.py
│   ├── requirements.txt
│   ├── database/
│   ├── mqtt_handler/
│   ├── routes/
│   └── data.db            (Auto-created)
├── esp32_garden_mqtt.py    ← Upload ke ESP32
└── README.md              (Dokumentasi utama)
```

---

## ⏱️ Waktu Setup Total

| Langkah | Waktu |
|---------|-------|
| 1. Verifikasi IP | 30 detik |
| 2. Update Konfigurasi | 1 menit |
| 3. Mulai MQTT | 30 detik |
| 4. Mulai Backend | 30 detik |
| 5. Verifikasi Backend | 1 menit |
| 6. Upload ESP32 | 2 menit |
| 7. Verifikasi Data | 2 menit |
| **Total** | **~8 menit** |

---

## ✅ Checklist Sebelum Production

- [ ] IP address diverifikasi dan diupdate
- [ ] WiFi SSID & password benar
- [ ] MQTT broker berjalan stabil
- [ ] Backend API responsif
- [ ] ESP32 terhubung ke MQTT
- [ ] Data mengalir ke database
- [ ] Pompa dapat dikontrol
- [ ] Servo dapat dikontrol
- [ ] Semua 5 sensor terdaftar

---

## 🎉 Selamat!

Sistem Anda sudah **siap digunakan**. 

Untuk langkah selanjutnya:
1. Kalibrasi sensor (optional)
2. Sesuaikan threshold otomasi
3. Integrasikan dengan frontend monorepo partner
4. Setup production deployment (Docker/Cloud)

---

**Pertanyaan?** Lihat folder `documentation` untuk panduan detail lainnya.

**Status**: ✅ Ready to Go! 🚀

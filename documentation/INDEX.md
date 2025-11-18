# 📚 Indeks Dokumentasi Project IoT Chili Garden

**Lokasi**: Folder `documentation/` dan `backend/`

---

## 🚀 MULAI DI SINI

### 1️⃣ **PANDUAN_MENJALANKAN.md** (START HERE!)
📍 **Lokasi**: `/documentation/PANDUAN_MENJALANKAN.md`  
⏱️ **Waktu**: 8 menit (step-by-step startup)  
📝 **Isi**:
- Persiapan IP address & WiFi
- Cara menjalankan MQTT Broker
- Cara menjalankan Flask Backend
- Cara upload ke ESP32
- Verifikasi semua komponen bekerja
- Troubleshooting cepat

**👉 BACA INI PERTAMA untuk menjalankan project!**

---

## 🔧 DOKUMENTASI TEKNIS

### 2️⃣ **ESP32_BACKEND_SYNC_GUIDE.md**
📍 **Lokasi**: `/backend/ESP32_BACKEND_SYNC_GUIDE.md`  
📖 **Jenis**: Technical Reference  
📝 **Isi**:
- MQTT Broker Configuration
- Topic Structure & Mappings
- Data Format & Field Names
- ADC Conversion Math
- Communication Flow Diagrams
- System Architecture Overview

**👉 BACA untuk memahami cara ESP32 & Backend berkomunikasi**

---

### 3️⃣ **API_DOCUMENTATION.md**
📍 **Lokasi**: `/backend/API_DOCUMENTATION.md`  
📖 **Jenis**: API Reference  
📝 **Isi**:
- 15+ REST API endpoints
- Request/response examples
- Status codes & error handling
- Authentication (jika ada)
- Rate limiting info

**👉 BACA untuk develop frontend atau integrasi**

---

### 4️⃣ **TESTING_GUIDE.md**
📍 **Lokasi**: `/backend/TESTING_GUIDE.md`  
📖 **Jenis**: Testing Reference  
📝 **Isi**:
- Unit test examples
- API integration tests
- MQTT message flow tests
- Database query tests

**👉 BACA untuk testing & quality assurance**

---

## 📋 VERIFIKASI & SETUP

### 5️⃣ **PRE_RUN_VALIDATION.md**
📍 **Lokasi**: `/backend/PRE_RUN_VALIDATION.md`  
📖 **Jenis**: Validation Checklist  
⏱️ **Waktu**: 5 menit (checklist)  
📝 **Isi**:
- Pre-run validation matrix
- All system checkpoints
- Go/No-Go decision matrix
- Detailed checklist items

**👉 BACA SEBELUM jalankan system untuk pertama kali**

---

### 6️⃣ **BACKEND_SETUP_SUMMARY.md**
📍 **Lokasi**: `/backend/BACKEND_SETUP_SUMMARY.md`  
📖 **Jenis**: Setup Summary  
📝 **Isi**:
- Backend folder structure
- All modules explanation
- Dependencies & versions
- Quick reference guides

**👉 BACA untuk understand backend architecture**

---

## 📊 STATUS & CHANGELOG

### 7️⃣ **SYSTEM_READY_SUMMARY.md**
📍 **Lokasi**: `/backend/SYSTEM_READY_SUMMARY.md`  
📖 **Jenis**: Status Report  
📝 **Isi**:
- What was fixed
- What was verified
- System readiness status
- Data flow diagrams

**👉 BACA untuk status apa aja yang udah siap**

---

### 8️⃣ **CHANGELOG.md**
📍 **Lokasi**: `/backend/CHANGELOG.md`  
📖 **Jenis**: Change History  
📝 **Isi**:
- All code changes made
- Before/after comparisons
- Line-by-line modifications
- Impact assessment

**👉 BACA untuk track semua perubahan yang dibuat**

---

## 🎯 QUICK REFERENCE

### 9️⃣ **QUICK_START.md**
📍 **Lokasi**: `/backend/QUICK_START.md`  
📖 **Jenis**: Quick Reference  
⏱️ **Waktu**: 5 menit (summary)  
📝 **Isi**:
- 5-step quick startup
- Status verification steps
- Common troubleshooting table
- Quick curl commands

**👉 BACA untuk quick reference & fast troubleshooting**

---

### 🔟 **README_DOCUMENTATION.md**
📍 **Lokasi**: `/backend/README_DOCUMENTATION.md`  
📖 **Jenis**: Documentation Navigator  
📝 **Isi**:
- Master documentation index
- Document relationships
- Learning paths
- Document summary table

**👉 BACA untuk navigasi semua dokumentasi**

---

## 📂 STRUKTUR FILE

```
project IoT UKL/
│
├── documentation/               ← DOKUMENTASI FOLDER
│   ├── PANDUAN_MENJALANKAN.md  ✅ START HERE (8 min step-by-step)
│   └── INDEX.md                 ← Anda berada di sini
│
├── backend/                     ← SOURCE CODE FOLDER
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── database/
│   │   ├── models.py
│   │   └── db_init.py
│   ├── mqtt_handler/
│   │   └── mqtt_client.py
│   ├── routes/
│   │   └── api.py
│   ├── static/
│   ├── templates/
│   ├── data.db
│   │
│   └── DOKUMENTASI BACKEND FOLDER:
│       ├── ESP32_BACKEND_SYNC_GUIDE.md
│       ├── API_DOCUMENTATION.md
│       ├── TESTING_GUIDE.md
│       ├── PRE_RUN_VALIDATION.md
│       ├── BACKEND_SETUP_SUMMARY.md
│       ├── SYSTEM_READY_SUMMARY.md
│       ├── CHANGELOG.md
│       └── README_DOCUMENTATION.md
│
├── esp32_garden_mqtt.py         ← ESP32 CODE (upload ke ESP32)
├── README.md
└── [other files]
```

---

## 🎓 LEARNING PATHS

### Path 1: "Saya ingin langsung menjalankan system"
```
1. PANDUAN_MENJALANKAN.md (8 min)
   ↓
2. Jalankan project
   ↓
3. QUICK_START.md (5 min, jika ada error)
```
⏱️ **Total**: ~15 menit

---

### Path 2: "Saya ingin understand how it works"
```
1. PANDUAN_MENJALANKAN.md (8 min)
   ↓
2. ESP32_BACKEND_SYNC_GUIDE.md (15 min)
   ↓
3. API_DOCUMENTATION.md (10 min)
   ↓
4. BACKEND_SETUP_SUMMARY.md (5 min)
```
⏱️ **Total**: ~40 menit

---

### Path 3: "Saya ingin develop & test"
```
1. PANDUAN_MENJALANKAN.md (8 min)
   ↓
2. API_DOCUMENTATION.md (10 min)
   ↓
3. TESTING_GUIDE.md (15 min)
   ↓
4. CHANGELOG.md (10 min - understand what changed)
```
⏱️ **Total**: ~45 menit

---

### Path 4: "Ada error, help!"
```
1. QUICK_START.md - Troubleshooting section (5 min)
   ↓
   ✓ Problem solved?
   ↓
2. PRE_RUN_VALIDATION.md (5 min)
   ↓
   ✓ Problem solved?
   ↓
3. PANDUAN_MENJALANKAN.md - Troubleshooting section (10 min)
   ↓
   ✓ Problem solved?
   ↓
4. ESP32_BACKEND_SYNC_GUIDE.md (15 min - deep dive)
```
⏱️ **Total**: ~35 menit

---

## 📞 QUICK LINKS

| Kebutuhan | Lihat File | Waktu |
|-----------|-----------|-------|
| Mulai project | PANDUAN_MENJALANKAN.md | 8 min |
| Ada error | QUICK_START.md | 5 min |
| API endpoints | API_DOCUMENTATION.md | 10 min |
| MQTT flow | ESP32_BACKEND_SYNC_GUIDE.md | 15 min |
| Verify system | PRE_RUN_VALIDATION.md | 5 min |
| Understand architecture | BACKEND_SETUP_SUMMARY.md | 5 min |
| See what changed | CHANGELOG.md | 10 min |
| System status | SYSTEM_READY_SUMMARY.md | 5 min |

---

## ⚡ INSTANT COMMANDS

### Mulai MQTT Broker
```powershell
mosquitto -p 1883
```

### Mulai Backend
```powershell
cd "c:\Users\Acer Nitro 5\Documents\TUGAS SMK TELKOM\TUGAS KELAS XII\project IoT UKL\backend"
python app.py
```

### Test Backend
```bash
curl http://192.168.0.186:5000/api/health
```

### Lihat data terbaru
```bash
curl http://192.168.0.186:5000/api/data/latest
```

### List semua sensor
```bash
curl http://192.168.0.186:5000/api/sensors
```

---

## ✅ STATUS

| Komponen | Status | Dokumentasi |
|----------|--------|-------------|
| Flask Backend | ✅ Ready | API_DOCUMENTATION.md |
| ESP32 Code | ✅ Ready | ESP32_BACKEND_SYNC_GUIDE.md |
| MQTT Integration | ✅ Ready | ESP32_BACKEND_SYNC_GUIDE.md |
| Database | ✅ Ready | BACKEND_SETUP_SUMMARY.md |
| All 5 Sensors | ✅ Ready | API_DOCUMENTATION.md |
| Pump Relay | ✅ Ready | API_DOCUMENTATION.md |
| Servo Motor | ✅ Ready | API_DOCUMENTATION.md |
| Data Sync | ✅ Verified | SYSTEM_READY_SUMMARY.md |
| API Endpoints | ✅ 15+ Ready | API_DOCUMENTATION.md |

---

## 🎯 NEXT STEPS

Setelah menjalankan project:

1. **Develop Frontend** (Partner team)
   - API base URL: `http://192.168.0.186:5000/api`
   - Endpoints reference: Lihat `API_DOCUMENTATION.md`

2. **Calibrate Sensors** (Optional)
   - Follow instructions di PANDUAN_MENJALANKAN.md

3. **Setup Automation** (Optional)
   - Edit rules di `backend/routes/api.py`

4. **Production Deployment** (Future)
   - Refer to Docker/Cloud documentation (belum dibuat)

---

## 📖 READING TIPS

- **Markdown Reader**: Buka file di VS Code atau text editor
- **Terminal Links**: Copy command langsung dari file
- **Timestamps**: Semua dokumentasi dated Nov 18, 2025
- **Version**: Backend v1.0, API v1.0, ESP32 firmware Nov 2025

---

**Last Updated**: November 18, 2025  
**Status**: ✅ Complete & Ready  
**Next**: Baca `PANDUAN_MENJALANKAN.md` untuk mulai! 🚀


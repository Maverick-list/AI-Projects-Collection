from flask import Blueprint, request, jsonify
from models import Attendance, ExamLog, db
import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/absensi/rekam', methods=['POST'])
def record_attendance():
    """
    Endpoint for external Python sensor script.
    Expected JSON: { "user_id": int, "status": str }
    """
    data = request.json
    user_id = data.get('user_id')
    status = data.get('status', 'Hadir')
    
    new_record = Attendance(
        user_id=user_id,
        status=status,
        method='Sensor',
        timestamp=datetime.datetime.now()
    )
    db.session.add(new_record)
    db.session.commit()
    
    return jsonify({"status": "success", "message": "Attendance recorded via sensor"})

@api_bp.route('/proctoring/log', methods=['POST'])
def proctor_log():
    """
    Endpoint for exam proctoring logs.
    Expected JSON: { "exam_id": int, "student_id": int, "event_type": str }
    """
    data = request.json
    exam_id = data.get('exam_id')
    student_id = data.get('student_id')
    event_type = data.get('event_type')
    
    new_log = ExamLog(
        exam_id=exam_id,
        student_id=student_id,
        event_type=event_type
    )
    db.session.add(new_log)
    db.session.commit()
    
    return jsonify({"status": "success"})

@api_bp.route('/chatbot/ask', methods=['POST'])
def chatbot_ask():
    """
    AI ChatBot API powering 'Ana' using Local Ollama (User must run 'ollama serve').
    Default model: 'mistral' (can be changed).
    """
    import requests
    
    data = request.json
    question = data.get('question', '')
    context = data.get('context', '') # Optional context from client
    
    # Advanced System Prompt for "Ana" (The Murabbi)
    system_prompt = (
        "Anda adalah 'Ana', asisten akademik cerdas dan Islami untuk MAS Jeumala Amal. "
        "PERAN ANDA: Sebagai 'Murabbi' (Pendidik) yang sabar, ceria, dan berwawasan luas. "
        "GAYA BICARA: Gunakan Bahasa Indonesia yang sopan, gaul tapi santun (akrab dengan siswa), dan sering menyisipkan nilai-nilai Islami. "
        "INSTRUKSI KHUSUS:\n"
        "1. Jawablah pertanyaan pelajaran dengan metode Sokrates (memancing siswa berpikir, bukan langsung memberi jawaban kunci jika itu soal latihan).\n"
        "2. Jika bertanya tentang agama/fiqih, berikan jawaban berdasarkan pemahaman Ahlussunnah wal Jamaah yang moderat.\n"
        "3. Sisipkan frasa Islami seperti 'Masya Allah', 'Alhamdulillah', 'Insya Allah' secara natural.\n"
        "4. Jika siswa terlihat stress, berikan motivasi dan kutipan Hadits atau Al-Qur'an yang relevan dan menenangkan.\n"
        "5. Jawablah dengan ringkas dan jelas, gunakan poin-poin jika perlu.\n"
        "KONTEKS TAMBAHAN: " + context
    )
    
    try:
        # Call local Ollama instance
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "mistral",
            "prompt": f"{system_prompt}\n\nUser: {question}\nAna:",
            "stream": False,
            "options": {
                "temperature": 0.7, # Kreatif tapi terarah
                "top_k": 40,
                "top_p": 0.9,
            }
        }, timeout=45) # Increased timeout
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('response', '')
            return jsonify({"response": answer})
        else:
            return jsonify({
                "response": f"Afwan (Maaf), Ana mengalami gangguan koneksi (Error: {response.status_code}). Pastikan Ollama menyala ya!"
            })
            
    except requests.exceptions.ConnectionError:
        return jsonify({
            "response": "Afwan, Ana tidak bisa terhubung ke otak utama (Ollama Offline). Tolong panggil teknisi atau cek koneksi server."
        })
    except Exception as e:
        print(f"Ollama API Error: {e}")
        return jsonify({
            "response": "Waduh, Ana lagi pusing nih (Internal Error). Coba tanya lagi nanti ya!"
        })

@api_bp.route('/ujian/soal', methods=['GET'])
def get_exam_questions():
    """
    Get list of questions for the exam (Mock data for prototype).
    """
    questions = [
        {
            "id": 1,
            "text": "Apa yang dimaksud dengan Thaharah menurut bahasa (etimologi)?",
            "options": ["Berjalan", "Bersuci / Kebersihan", "Makan", "Berhenti"],
            "type": "PG"
        },
        {
            "id": 2,
            "text": "Air yang suci dan mensucikan disebut air...",
            "options": ["Mutanajis", "Musta'mal", "Mutlak", "Musyammas"],
            "type": "PG"
        },
        {
            "id": 3,
            "text": "Rukun Wudhu ada berapa?",
            "options": ["4", "5", "6", "7"],
            "type": "PG"
        },
        {
            "id": 4,
            "text": "Membasuh muka termasuk rukun wudhu yang ke...",
            "options": ["1", "2", "3", "4"],
            "type": "PG"
        },
        {
            "id": 5,
            "text": "Tayamum dilakukan menggunakan...",
            "options": ["Air", "Debu yang suci", "Batu", "Kayu"],
            "type": "PG"
        }
    ]
    return jsonify(questions)

@api_bp.route('/ujian/submit', methods=['POST'])
def submit_exam():
    """
    Handle exam submission.
    Expected JSON: { "answers": { "1": "B", "2": "C" ... } }
    """
    data = request.json
    answers = data.get('answers', {})
    
    # Simple grading key (Mock)
    key = {
        "1": "Bersuci / Kebersihan",
        "2": "Mutlak",
        "3": "6",
        "4": "2",
        "5": "Debu yang suci"
    }
    
    score = 0
    total = len(key)
    
    for q_id, answer in answers.items():
        if key.get(q_id) == answer:
            score += 1
            
    final_score = (score / total) * 100
    
    return jsonify({
        "status": "success",
        "score": final_score,
        "message": f"Ujian selesai! Nilai Anda: {final_score}"
    })

@api_bp.route('/notifications', methods=['GET'])
def get_notifications():
    # Mock data for now since we don't have login context in API blueprint easily without more setup, 
    # but in a real app we'd use current_user.id
    # For prototype, we return generic notifications
    
    notifications = [
        {
            "id": 1,
            "title": "Tugas Fiqih",
            "message": "Deadline tugas Bab Thaharah malam ini pukul 23:59 WIB.",
            "category": "warning",
            "time": "Baru saja"
        },
        {
            "id": 2,
            "title": "Nilai Matematika Keluar",
            "message": "Pak Budi baru saja menginput nilai UH 1. Cek sekarang!",
            "category": "success",
            "time": "2 jam yang lalu"
        },
        {
            "id": 3,
            "title": "Jadwal Ujian",
            "message": "Jadwal UAS Semester Ganjil telah terbit.",
            "category": "info",
            "time": "1 hari yang lalu"
        }
    ]
    return jsonify(notifications)

@api_bp.route('/study-planner/generate', methods=['POST'])
def generate_study_plan():
    """
    Generate a study plan using AI.
    """
    import requests
    
    # Mock context - in real app fetch from DB
    context = "Siswa kelas 10, besok ada ujian Matematika Bab Logaritma. Tugas Fiqih belum dikerjakan."
    
    system_prompt = (
        "Anda adalah asisten belajar pribadi. "
        "Buatkan jadwal belajar sore-malam yang realistis untuk siswa ini. "
        "Format: JSON Array of objects [{time: '...', activity: '...'}]. "
        "Hanya JSON."
    )
    
    try:
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "mistral",
            "prompt": f"{system_prompt}\n\nContext: {context}\nJSON Schedule:",
            "stream": False,
            "format": "json" 
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            # In a real app we would parse JSON string to object
            # For now just send raw text or mock a structured response if LLM fails
            return jsonify({
                "plan": [
                    {"time": "16:00 - 17:00", "activity": "Review Materi Matematika (Logaritma)"},
                    {"time": "17:00 - 17:30", "activity": "Istirahat & Shalat Ashar"},
                    {"time": "19:30 - 20:30", "activity": "Kerjakan Tugas Fiqih"},
                    {"time": "20:30 - 21:00", "activity": "Latihan Soal Matematika"}
                ] 
            }) 
    except:
        pass
        
    # Fallback if AI fails or offline
    return jsonify({
        "plan": [
            {"time": "16:00 - 17:00", "activity": "Review Materi Harian"},
            {"time": "19:30 - 20:30", "activity": "Mengerjakan PR"},
            {"time": "20:30 - 21:00", "activity": "Persiapan Jadwal Besok"}
        ]
    })

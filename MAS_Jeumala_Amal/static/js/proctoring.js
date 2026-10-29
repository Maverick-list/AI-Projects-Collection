/**
 * MAS Jeumala Amal - Proctoring Logic
 * Handles tab focus, visibility, and basic webcam movement simulation for logs.
 */

document.addEventListener('DOMContentLoaded', async () => {
    const video = document.getElementById('webcam');
    const proctorLogs = document.getElementById('proctor-logs');

    // 1. Setup Webcam
    if (video) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
        } catch (err) {
            addLog('❌ Gagal mengakses kamera. Izin diperlukan!', 'red');
        }
    }

    // 2. Visibility API (Tab Switching)
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            recordViolation('tab_switch', 'Pindah tab terdeteksi!');
        }
    });

    // 3. Focus Event (Minimize Window)
    window.addEventListener('blur', () => {
        recordViolation('window_blur', 'Keluar dari jendela ujian!');
    });

    // 4. Helper: Record Violation
    async function recordViolation(type, message) {
        addLog(`⚠️ ${message}`, 'amber');

        try {
            await fetch('/api/proctoring/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    exam_id: 1, // Mock exam id
                    student_id: 1, // Will be fetched from session in real backend
                    event_type: type
                })
            });
        } catch (e) {
            console.error('Failed to log violation', e);
        }
    }

    // 5. Helper: Add Log UI
    function addLog(msg, color) {
        const div = document.createElement('div');
        div.className = `flex items-center gap-3 text-xs text-${color}-600 font-semibold bg-${color}-50 p-2 rounded-lg anime-fade-in`;
        div.innerHTML = `<span>⚠️</span> ${msg}`;
        proctorLogs.prepend(div);
    }
});

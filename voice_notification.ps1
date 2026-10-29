Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Speak('Maaf ya, karena saya AI yang berjalan di latar belakang, saya tidak punya izin untuk memunculkan jendela aplikasi ke layar Anda. Tolong ketik perintahnya langsung di terminal VS Code.')

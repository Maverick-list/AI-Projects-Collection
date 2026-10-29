import os

class WebExporter:
    def __init__(self, record_dir="recordings"):
        self.record_dir = record_dir
        self.output_file = "gesture_report.html"

    def export(self):
        videos = [f for f in os.listdir(self.record_dir) if f.endswith(".mp4")]
        
        html = f"""
        <html>
        <head>
            <title>Gesture Translation Report</title>
            <style>
                body {{ font-family: sans-serif; background: #1a1a1a; color: white; padding: 20px; }}
                .video-card {{ background: #333; padding: 15px; margin-bottom: 20px; border-radius: 8px; }}
                video {{ width: 100%; max-width: 600px; }}
            </style>
        </head>
        <body>
            <h1>Gesture Session Report</h1>
            <div class="gallery">
        """
        
        for vid in videos:
            html += f"""
                <div class="video-card">
                    <h3>Session: {vid}</h3>
                    <video controls src="{os.path.join(self.record_dir, vid)}"></video>
                </div>
            """
            
        html += """
            </div>
        </body>
        </html>
        """
        
        with open(self.output_file, "w") as f:
            f.write(html)
        print(f"Web report exported to {self.output_file}")

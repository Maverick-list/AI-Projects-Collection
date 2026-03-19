from flask import Blueprint, send_file, request, jsonify
from models import User, db
import io

# We'll use this for export functions
api_extra_bp = Blueprint('api_extra', __name__)

@api_extra_bp.route('/export/murid/csv')
def export_murid_csv():
    murid_data = User.query.filter_by(role='student').all()
    data = []
    for m in murid_data:
        data.append({
            "Nama": m.nama,
            "NIS": m.nis,
            "Kelas": m.kelas,
            "Email": m.email,
            "Kontak Ortu": m.parent_contact
        })
    import pandas as pd
    df = pd.DataFrame(data)
    csv_data = df.to_csv(index=False)
    return send_file(
        io.BytesIO(csv_data.encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='data_murid_jeumala.csv'
    )

# PDF Generation placeholder (simplified)
@api_extra_bp.route('/rapor/download/<int:student_id>')
def download_rapor_pdf(student_id):
    from fpdf import FPDF
    student = User.query.get(student_id)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(40, 10, f"RAPOR DIGITAL - MAS JEUMALA AMAL")
    pdf.ln(20)
    pdf.set_font("Arial", '', 12)
    pdf.cell(40, 10, f"Nama: {student.nama}")
    pdf.ln(10)
    pdf.cell(40, 10, f"NIS: {student.nis}")
    pdf.ln(10)
    pdf.cell(40, 10, f"Kelas: {student.kelas}")
    pdf.ln(20)
    pdf.cell(40, 10, "Nilai Akademik:")
    pdf.ln(10)
    pdf.cell(40, 10, "- Fiqih: 85 (A)")
    pdf.ln(10)
    pdf.cell(40, 10, "- Matematika: 80 (B)")
    
    return send_file(
        io.BytesIO(pdf.output(dest='S').encode('latin1')),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'rapor_{student.nis}.pdf'
    )

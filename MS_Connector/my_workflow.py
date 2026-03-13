from probuildiq_reportlab_generator import ProBuildIQPDFGenerator

# Your FEZ file
fez_file = "B_Down_-_1x1.fez"

# Generate PDF
with ProBuildIQPDFGenerator(fez_file) as gen:
    gen.generate_pdf("output.pdf")

print("Done!")
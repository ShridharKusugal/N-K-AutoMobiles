from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch

def create_flowchart_pdf(filename="NK_Automobiles_Flowchart.pdf"):
    c = canvas.Canvas(filename, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # Background
    c.setFillColorRGB(0.05, 0.05, 0.1)
    c.rect(0, 0, width, height, fill=1)
    
    # Title
    c.setFont("Helvetica-Bold", 32)
    c.setStrokeColor(colors.white)
    c.setFillColor(colors.white)
    c.drawCentredString(width/2, height - 1*inch, "NK Automobiles")
    
    c.setFont("Helvetica", 14)
    c.setFillColorRGB(0.7, 0.7, 0.7)
    c.drawCentredString(width/2, height - 1.4*inch, "USER JOURNEY FLOWCHART")
    
    # Flowchart Logic
    steps = [
        "Start\n(Home Page)",
        "Browse /\nSearch Products",
        "Add to Cart /\nView Details",
        "Login /\nRegister",
        "Checkout\n(Address)",
        "Payment\n(UPI/COD)",
        "Order\nConfirmed"
    ]
    
    # Node Settings
    nodes_count = len(steps)
    node_width = 1.3 * inch
    node_height = 0.9 * inch
    spacing = 0.15 * inch
    total_width = (nodes_count * node_width) + ((nodes_count-1) * spacing)
    start_x = (width - total_width) / 2
    y = height / 2 - (node_height / 2)
    
    # Draw Nodes and Connectors
    for i, step in enumerate(steps):
        x = start_x + (i * (node_width + spacing))
        
        # Connector
        if i < nodes_count - 1:
            conn_x = x + node_width
            conn_y = y + node_height/2
            c.setStrokeColorRGB(1, 0.3, 0.3)
            c.setLineWidth(2)
            c.line(conn_x, conn_y, conn_x + spacing, conn_y)
            
            # Arrow head
            c.line(conn_x + spacing, conn_y, conn_x + spacing - 5, conn_y + 3)
            c.line(conn_x + spacing, conn_y, conn_x + spacing - 5, conn_y - 3)

        # Gradient-like box
        c.setStrokeColorRGB(0.5, 0.5, 0.5)
        c.setLineWidth(1)
        
        # Last node is special (Green-ish)
        if i == nodes_count - 1:
            c.setFillColorRGB(0.1, 0.4, 0.1)
        else:
            c.setFillColorRGB(0.15, 0.15, 0.25)
            
        c.roundRect(x, y, node_width, node_height, 8, fill=1)
        
        # Text
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold" if i == nodes_count-1 else "Helvetica", 10)
        
        lines = step.split('\n')
        line_y = y + node_height/2 + (len(lines)-1)*6
        for line in lines:
            c.drawCentredString(x + node_width/2, line_y, line)
            line_y -= 12

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawCentredString(width/2, 0.5 * inch, "Generated for NK Automobiles Project Report | 2026")
    
    c.save()
    print(f"PDF saved as {filename}")

if __name__ == "__main__":
    create_flowchart_pdf()

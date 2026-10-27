import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation(output_path="NK_Automobiles_MCA_Project_Presentation.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette - Executive Automobile Theme
    COLOR_NAVY_DARK = RGBColor(15, 31, 56)       # #0F1F38 Deep Navy Blue
    COLOR_NAVY_MID = RGBColor(30, 58, 95)        # #1E3A5F Steel Blue
    COLOR_ACCENT_RED = RGBColor(211, 47, 47)     # #D32F2F Automotive Red
    COLOR_ACCENT_BLUE = RGBColor(24, 119, 242)   # #1877F2 Tech Blue
    COLOR_BG_LIGHT = RGBColor(246, 248, 252)     # #F6F8FC Light Canvas
    COLOR_WHITE = RGBColor(255, 255, 255)        # #FFFFFF Card background
    COLOR_TEXT_DARK = RGBColor(30, 41, 59)       # #1E293B Primary text
    COLOR_TEXT_MUTED = RGBColor(100, 116, 139)   # #64748B Secondary text
    COLOR_BORDER = RGBColor(226, 232, 240)       # #E2E8F0 Subtle outline
    COLOR_CARD_HEADER = RGBColor(241, 245, 249)  # #F1F5F9 Container header
    COLOR_SUCCESS = RGBColor(16, 149, 106)       # #10956A Green badge
    COLOR_HIGHLIGHT = RGBColor(238, 242, 255)    # #EEF2FF Soft Indigo Card

    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide, color=COLOR_BG_LIGHT):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_badge="MCA PROJECT PRESENTATION"):
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.95))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_badge = tf.paragraphs[0]
        p_badge.text = category_badge.upper()
        p_badge.font.name = "Calibri"
        p_badge.font.size = Pt(10)
        p_badge.font.bold = True
        p_badge.font.color.rgb = COLOR_ACCENT_RED
        
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.name = "Calibri"
        p_title.font.size = Pt(21)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_NAVY_DARK
        p_title.space_before = Pt(2)

    def add_card(slide, left, top, width, height, title=None, bg_color=COLOR_WHITE, border_color=COLOR_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.2)
        else:
            card.line.fill.background()
        
        if title:
            title_box = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.18), Inches(width - 0.5), Inches(0.45))
            tf = title_box.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = "Calibri"
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = COLOR_NAVY_DARK
        
        return card

    def add_bullet_list(slide, left, top, width, height, items, font_size=11.5, text_color=COLOR_TEXT_DARK):
        txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
        tf = txBox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        for i, item in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            if i > 0:
                p.space_before = Pt(7)
                
            p.font.name = "Calibri"
            p.font.size = Pt(font_size)
            
            if isinstance(item, tuple):
                run1 = p.add_run()
                run1.text = "• " + item[0] + ": "
                run1.font.bold = True
                run1.font.color.rgb = COLOR_NAVY_MID
                run2 = p.add_run()
                run2.text = item[1]
                run2.font.bold = False
                run2.font.color.rgb = text_color
            elif ":" in item:
                parts = item.split(":", 1)
                run1 = p.add_run()
                run1.text = "• " + parts[0].strip() + ": "
                run1.font.bold = True
                run1.font.color.rgb = COLOR_NAVY_MID
                run2 = p.add_run()
                run2.text = parts[1].strip()
                run2.font.bold = False
                run2.font.color.rgb = text_color
            else:
                run = p.add_run()
                run.text = "• " + item
                run.font.bold = False
                run.font.color.rgb = text_color

    def set_speaker_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    # ==========================================
    # SLIDE 1: TITLE SLIDE (Dark Executive Theme)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, COLOR_NAVY_DARK)

    # Accent Red Top Bar
    top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.7), Inches(11.733), Inches(0.08))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = COLOR_ACCENT_RED
    top_bar.line.fill.background()

    # Title & Subtitle box
    tbox = s1.shapes.add_textbox(Inches(0.8), Inches(1.1), Inches(11.733), Inches(2.2))
    tf1 = tbox.text_frame
    tf1.word_wrap = True
    
    p0 = tf1.paragraphs[0]
    p0.text = "MASTER OF COMPUTER APPLICATIONS (MCA) PROJECT VIVA PRESENTATION"
    p0.font.name = "Calibri"
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(148, 163, 184)

    p1 = tf1.add_paragraph()
    p1.text = "NK AUTOMOBILES"
    p1.font.name = "Calibri"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p1.space_before = Pt(6)

    p2 = tf1.add_paragraph()
    p2.text = "Vehicle Inventory and Management System with Two-Wheeler Fitment Engine"
    p2.font.name = "Calibri"
    p2.font.size = Pt(17)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.space_before = Pt(4)

    # Card 1: Student Details
    c1 = add_card(s1, 0.8, 3.7, 5.7, 2.8, bg_color=RGBColor(24, 43, 73), border_color=RGBColor(45, 74, 117))
    t1 = s1.shapes.add_textbox(Inches(1.05), Inches(3.9), Inches(5.2), Inches(2.4))
    tf_c1 = t1.text_frame
    tf_c1.word_wrap = True
    
    p = tf_c1.paragraphs[0]
    p.text = "PROJECT DEVELOPERS"
    p.font.name = "Calibri"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_RED
    
    p = tf_c1.add_paragraph()
    p.text = "• Shridhar Kusugal  (USN: 2XXMCAXXX)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(8)

    p = tf_c1.add_paragraph()
    p.text = "• Mohammad Kaif  (USN: 2XXMCAXXX)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(4)

    p = tf_c1.add_paragraph()
    p.text = "Course: Master of Computer Applications (MCA)\nAcademic Year: 2025 – 2026"
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(148, 163, 184)
    p.space_before = Pt(12)

    # Card 2: Institution & Guide Details
    c2 = add_card(s1, 6.8, 3.7, 5.7, 2.8, bg_color=RGBColor(24, 43, 73), border_color=RGBColor(45, 74, 117))
    t2 = s1.shapes.add_textbox(Inches(7.05), Inches(3.9), Inches(5.2), Inches(2.4))
    tf_c2 = t2.text_frame
    tf_c2.word_wrap = True

    p = tf_c2.paragraphs[0]
    p.text = "INSTITUTION & GUIDANCE"
    p.font.name = "Calibri"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_RED

    p = tf_c2.add_paragraph()
    p.text = "Chetan Business School"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(8)

    p = tf_c2.add_paragraph()
    p.text = "Department of MCA, Hubballi, Karnataka"
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_before = Pt(2)

    p = tf_c2.add_paragraph()
    p.text = "Project Guide: [Prof. / Dr. Project Guide Name]\nDesignation: [Assistant Professor / HOD, Dept. of MCA]"
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(148, 163, 184)
    p.space_before = Pt(12)

    set_speaker_notes(s1, 
        "Good morning respected external examiners, project guide, and faculty members. "
        "We are Shridhar Kusugal and Mohammad Kaif, final year MCA students at Chetan Business School, Hubballi. "
        "Today, we are proud to present our MCA software project titled 'NK Automobiles – Vehicle Inventory and Management System'. "
        "This is an end-to-end web-based automobile inventory, customer sales, and vehicle fitment platform developed specifically for "
        "automobile spare parts dealerships and service centers."
    )

    # ==========================================
    # SLIDE 2: INTRODUCTION & OVERVIEW
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Introduction & Project Overview", "Project Background")

    add_card(s2, 0.8, 1.5, 3.7, 5.4, "Industry Context", bg_color=COLOR_WHITE)
    add_bullet_list(s2, 1.05, 2.1, 3.2, 4.5, [
        ("Automobile Retail", "Retail automobile spare parts in India is a high-volume, multi-brand industry requiring precise fitment."),
        ("Hubballi Enterprise", "NK Automobiles operates as an established multi-brand two-wheeler spare parts hub in Hubballi, Karnataka."),
        ("Digital Shift", "Traditional paper-based ledger systems struggle with expanding catalogs, stock verification, and rapid billing."),
        ("Scale of Operation", "The enterprise caters to hundreds of mechanics, vehicle owners, and retail customers daily.")
    ], font_size=11)

    add_card(s2, 4.8, 1.5, 3.7, 5.4, "System Purpose", bg_color=COLOR_WHITE)
    add_bullet_list(s2, 5.05, 2.1, 3.2, 4.5, [
        ("Unified Portal", "Centralize spare-parts inventory, sales processing, and customer requests into one responsive web portal."),
        ("Part Compatibility", "Eliminate part mismatch by mapping spare parts directly to verified two-wheeler models."),
        ("Frictionless Sales", "Enable customers and mechanics to browse 181+ verified parts and complete orders via Guest Checkout."),
        ("UPI Integration", "Incorporate modern dynamic UPI QR scan-to-pay workflow for instant digital payment verification.")
    ], font_size=11)

    add_card(s2, 8.8, 1.5, 3.7, 5.4, "Key Highlights", bg_color=COLOR_WHITE)
    add_bullet_list(s2, 9.05, 2.1, 3.2, 4.5, [
        ("181 Active Products", "Spanning 8 automotive categories (Engine, Brake, Chains, Electricals, Filters, etc.)."),
        ("1,650+ Compatibility Rules", "Authentic vehicle mapping across 11 popular Indian bike & scooter models."),
        ("Role-Based Security", "Separate secure interfaces for Customers and Admin management."),
        ("Full-Stack Architecture", "Built with lightweight Python Flask, MySQL 8.0, and responsive Bootstrap 5.")
    ], font_size=11)

    set_speaker_notes(s2,
        "To begin with our project overview: NK Automobiles is an active automobile enterprise in Hubballi. "
        "In the two-wheeler spares industry, the biggest operational bottleneck is not just keeping stock, but knowing which part fits which bike. "
        "A clutch cable made for a Pulsar will never fit a Hero Splendor, and automatic scooters like Honda Activa don't use manual clutch cables at all! "
        "Our system brings complete digital transformation to NK Automobiles: a unified web portal managing 181 parts, over 1,650 verified vehicle compatibility "
        "rules, an interactive customer storefront, and a robust administrative control hub."
    )

    # ==========================================
    # SLIDE 3: PROBLEM STATEMENT
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Problem Statement: Challenges in Manual Operations", "Operational Challenges")

    add_card(s3, 0.8, 1.5, 5.7, 2.55, "1. Incompatible Part Mismatches & Returns", bg_color=COLOR_WHITE)
    add_bullet_list(s3, 1.05, 2.1, 5.2, 1.8, [
        ("Lack of Fitment Verification", "Customers frequently purchase wrong parts due to subtle model year or emission (BS3/BS4/BS6) variations."),
        ("High Return Overhead", "Part returns cause inventory discrepancies, wasted counter time, and customer dissatisfaction.")
    ], font_size=11)

    add_card(s3, 6.8, 1.5, 5.7, 2.55, "2. Fragmented Stock & Sudden Stockouts", bg_color=COLOR_WHITE)
    add_bullet_list(s3, 7.05, 2.1, 5.2, 1.8, [
        ("Manual Ledger Tracking", "Inventory records maintained in physical books or isolated spreadsheets are prone to manual logging errors."),
        ("Zero Low-Stock Visibility", "Shop owners discover stockouts only when a customer physically asks for a part at the counter.")
    ], font_size=11)

    add_card(s3, 0.8, 4.35, 5.7, 2.55, "3. Slow Counter Checkout & Billing Bottlenecks", bg_color=COLOR_WHITE)
    add_bullet_list(s3, 1.05, 4.95, 5.2, 1.8, [
        ("Handwritten Invoices", "Manual billing creates long queues during peak morning and evening mechanic rush hours."),
        ("Lost Customer History", "No digital record of past repairs, repeat customer buying habits, or warranty tracking.")
    ], font_size=11)

    add_card(s3, 6.8, 4.35, 5.7, 2.55, "4. Payment Reconciliation & Audit Deficits", bg_color=COLOR_WHITE)
    add_bullet_list(s3, 7.05, 4.95, 5.2, 1.8, [
        ("Disjointed Payment Tracking", "Cash transactions combined with personal UPI QR scans lead to daily cash-drawer mismatch."),
        ("Lack of Activity Audit", "No audit log exists to identify who altered stock quantities or issued discounts.")
    ], font_size=11)

    set_speaker_notes(s3,
        "Here we articulate the core problem statement. In traditional automobile shops, four critical pain points exist. "
        "First, the fitment problem: two-wheeler parts change across model years and BS emission variants. Customers often buy incorrect parts, leading to high return rates. "
        "Second, inventory is scattered across ledgers, causing unexpected stockouts. "
        "Third, manual handwritten billing creates slow counter queues and loses customer purchase history. "
        "Finally, payment reconciliation between cash and personal UPI codes creates end-of-day accounting errors without audit trails."
    )

    # ==========================================
    # SLIDE 4: OBJECTIVES OF THE SYSTEM
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Project Objectives & Scope", "Project Goals")

    objectives = [
        ("Centralized Catalog & Inventory", "Develop a relational database-backed catalog storing 181+ verified parts with real-time stock and pricing tracking."),
        ("Intelligent Fitment Search Engine", "Implement dynamic vehicle compatibility mapping across 11 key Indian motorcycle & scooter platforms with live filtering."),
        ("Streamlined Customer Storefront", "Provide a fast, responsive e-commerce interface with category filtering, live search, cart calculation, and Guest Checkout."),
        ("Integrated UPI Digital Payments", "Generate dynamic, order-specific UPI QR codes allowing seamless scan-to-pay functionality on mobile and desktop."),
        ("Admin Control & Security", "Establish role-based access control, product CRUD operations, verified image asset management, and system activity logs.")
    ]

    for i, (title, desc) in enumerate(objectives):
        top_y = 1.5 + (i * 1.08)
        c = add_card(s4, 0.8, top_y, 11.733, 0.95, bg_color=COLOR_WHITE)
        
        # Number badge
        num_box = s4.shapes.add_shape(MSO_SHAPE.OVAL, Inches(1.0), Inches(top_y + 0.18), Inches(0.58), Inches(0.58))
        num_box.fill.solid()
        num_box.fill.fore_color.rgb = COLOR_NAVY_MID
        num_box.line.fill.background()
        tf_n = num_box.text_frame
        p_n = tf_n.paragraphs[0]
        p_n.text = f"0{i+1}"
        p_n.font.size = Pt(13)
        p_n.font.bold = True
        p_n.font.color.rgb = COLOR_WHITE
        p_n.alignment = PP_ALIGN.CENTER
        
        # Text
        tx = s4.shapes.add_textbox(Inches(1.8), Inches(top_y + 0.15), Inches(10.5), Inches(0.65))
        tf = tx.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.bold = True
        p1.font.size = Pt(13)
        p1.font.color.rgb = COLOR_NAVY_DARK
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(2)

    set_speaker_notes(s4,
        "Based on these challenges, we established five definitive project objectives. "
        "First, create a centralized digital inventory for 181+ parts. "
        "Second, build an intelligent compatibility engine so customers can verify if a part fits their specific bike before ordering. "
        "Third, engineer a frictionless customer interface featuring guest checkout, allowing customers to order without lengthy registrations. "
        "Fourth, provide automated UPI QR generation for instant payments. "
        "Fifth, give the store owner an administrative dashboard with stock adjustment tools and audit logging."
    )

    # ==========================================
    # SLIDE 5: EXISTING SYSTEM VS PROPOSED SYSTEM
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Existing System vs. Proposed System", "System Comparison")

    # Table layout
    rows, cols = 7, 3
    left, top, width, height = Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.4)
    table_shape = s5.shapes.add_table(rows, cols, left, top, width, height)
    tbl = table_shape.table

    tbl.columns[0].width = Inches(2.3)
    tbl.columns[1].width = Inches(4.6)
    tbl.columns[2].width = Inches(4.833)

    table_data = [
        ("Evaluation Parameter", "Existing Manual / Legacy System", "Proposed NK Automobiles System"),
        ("Inventory Tracking", "Physical stock registers or static Excel sheets; stock levels frequently out of sync.", "Centralized MySQL 8.0 database; automated atomic stock deduction upon order completion."),
        ("Part Compatibility", "Relies entirely on counter staff memory; high rate of wrong part sales.", "Engineered Two-Wheeler Compatibility Engine with 1,655+ rules and live bike search."),
        ("Customer Access", "Restricted to physical storefront counter during working business hours.", "24/7 web access across smartphones and desktop devices with responsive UI."),
        ("Checkout & Ordering", "Handwritten bill slips; mandatory queue; no digital order record.", "Frictionless Guest Checkout and authenticated portal with order tracking."),
        ("Payment Reconciliation", "Loose cash handling or unverified manual UPI screenshots.", "Order-tagged dynamic UPI QR codes with UTR reference validation."),
        ("Security & Auditing", "Zero access control; registers vulnerable to physical loss or tampering.", "Bcrypt/Werkzeug password hashing, session RBAC, and dedicated system_logs.")
    ]

    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.text = val
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.font.name = "Calibri"
            
            if r_idx == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_NAVY_DARK
                p.font.bold = True
                p.font.size = Pt(12)
                p.font.color.rgb = COLOR_WHITE
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_WHITE if r_idx % 2 == 1 else RGBColor(248, 250, 252)
                p.font.size = Pt(10)
                p.font.color.rgb = COLOR_TEXT_DARK
                if c_idx == 0:
                    p.font.bold = True
                    p.font.color.rgb = COLOR_NAVY_MID
                elif c_idx == 2:
                    p.font.color.rgb = RGBColor(15, 95, 60)

    set_speaker_notes(s5,
        "Slide 5 provides a structured comparison between the existing manual process and our proposed web application. "
        "Notice the major contrasts: While the legacy system relies on paper ledgers and counter staff guesswork, "
        "NK Automobiles provides automated real-time inventory tracking and a verified fitment engine. "
        "Furthermore, our system replaces handwritten billing with guest checkout and dynamic UPI QR generation, "
        "and replaces vulnerable paper records with an ACID-compliant MySQL database protected by session authentication and system audit logs."
    )

    # ==========================================
    # SLIDE 6: TECHNOLOGY STACK
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Technology Stack & Development Environment", "System Implementation")

    # 4 Tech Cards
    tech_data = [
        ("Backend Technologies", [
            ("Language", "Python 3.12+ (Robust, efficient, highly readable)"),
            ("Framework", "Flask (Lightweight, modular WSGI web framework)"),
            ("Security Engine", "Werkzeug Security (SHA-256 / PBKDF2 password hashing)"),
            ("Architecture", "Model-View-Controller (MVC) server pattern"),
            ("Session Management", "Flask Client-side cryptographically signed sessions")
        ]),
        ("Database Tier", [
            ("RDBMS Engine", "MySQL 8.0 Community Server"),
            ("Python Driver", "mysql-connector-python (Official Oracle driver)"),
            ("Data Integrity", "ACID transactions with foreign key constraints"),
            ("Query Pattern", "Strictly Parameterized SQL queries (Zero SQL injection)"),
            ("Database Scale", "14 relational tables, 181 products, 1,655 mappings")
        ]),
        ("Frontend & User Interface", [
            ("Core Markup", "Semantic HTML5 with SEO meta tags"),
            ("Styling Framework", "Bootstrap 5.3 (Mobile-first responsive grid system)"),
            ("Client Scripting", "Vanilla JavaScript (ES6+) for DOM manipulation & search"),
            ("Template Engine", "Jinja2 (Server-side dynamic template rendering)"),
            ("Icons & Assets", "FontAwesome 6.4 + High-res verified part photography")
        ]),
        ("Tools & Environment", [
            ("IDE / Editor", "Visual Studio Code with Python & SQL extensions"),
            ("Local Server", "XAMPP / MySQL Service on port 3306"),
            ("Version Control", "Git & GitHub for source code management"),
            ("API Testing", "Postman & Python unittest suite"),
            ("Image Processing", "Pillow (PIL) for image optimization & verification")
        ])
    ]

    for i, (cat_title, items) in enumerate(tech_data):
        col = i % 2
        row = i // 2
        cx = 0.8 + (col * 6.0)
        cy = 1.5 + (row * 2.8)
        
        add_card(s6, cx, cy, 5.7, 2.65, cat_title, bg_color=COLOR_WHITE)
        add_bullet_list(s6, cx + 0.25, cy + 0.6, 5.2, 1.9, items, font_size=10.5)

    set_speaker_notes(s6,
        "On Slide 6, we present the technology stack used in building NK Automobiles. "
        "For the backend, we chose Python with the Flask web framework. Flask is lightweight, highly modular, and provides full control over routing and security without the heavy overhead of monolithic frameworks. "
        "For data storage, we used MySQL 8.0 with the official mysql-connector-python driver. Every single query is strictly parameterized to prevent SQL injection vulnerabilities. "
        "On the frontend, we implemented responsive Bootstrap 5.3, semantic HTML5, modern ES6 JavaScript for instant client-side filtering, and Jinja2 server-side templating. "
        "Development was conducted using VS Code, Git version control, and Python's built-in unittest framework."
    )

    # ==========================================
    # SLIDE 7: SYSTEM ARCHITECTURE (3-Tier Model)
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "System Architecture: 3-Tier Web Architecture", "System Design")

    # Tier 1 Card (Top)
    c_t1 = add_card(s7, 0.8, 1.5, 11.733, 1.55, "Tier 1: Presentation Layer (Client Tier)", bg_color=COLOR_WHITE)
    add_bullet_list(s7, 1.05, 2.05, 11.2, 0.9, [
        ("User Devices", "Mobile Smartphones, Tablets, Desktop Web Browsers accessing HTTP/HTTPS endpoints."),
        ("Frontend Technologies", "Bootstrap 5 Responsive Grid, HTML5 Semantic Layouts, CSS3 Transitions, FontAwesome Icons."),
        ("Client-Side Logic", "JavaScript Event Listeners (Live vehicle search, cart item quantity adjuster, dynamic modal popups, form validation).")
    ], font_size=10.5)

    # Tier 2 Card (Middle)
    c_t2 = add_card(s7, 0.8, 3.25, 11.733, 1.85, "Tier 2: Application & Business Logic Layer (Python Flask Server)", bg_color=COLOR_HIGHLIGHT, border_color=COLOR_ACCENT_BLUE)
    add_bullet_list(s7, 1.05, 3.8, 11.2, 1.2, [
        ("WSGI Controller (app.py)", "Central routing engine managing 25+ endpoints (/products, /product/<id>, /checkout, /admin)."),
        ("Authentication & Security", "Werkzeug password hashing, session-based role checks (is_admin), CSRF protection & input sanitization."),
        ("Core Business Engines", "Two-Wheeler Compatibility Engine, Coupon Discount Calculator, Guest Checkout Handler, UPI QR Generator."),
        ("Template & API Pipeline", "Jinja2 server-side HTML rendering engine + JSON response serialisation for asynchronous requests.")
    ], font_size=10.5)

    # Tier 3 Card (Bottom)
    c_t3 = add_card(s7, 0.8, 5.3, 11.733, 1.65, "Tier 3: Database & Persistence Layer (MySQL 8.0)", bg_color=COLOR_WHITE)
    add_bullet_list(s7, 1.05, 5.85, 11.2, 1.0, [
        ("Relational Storage", "14 normalized tables executing ACID-compliant transactional operations."),
        ("Query Interface (db_queries.py)", "Modular database access layer using mysql.connector with connection recycling & parameterized queries."),
        ("Data Consistency", "Foreign key constraints cascading parent-child integrity across orders, order_items, and compatibility lists.")
    ], font_size=10.5)

    set_speaker_notes(s7,
        "Slide 7 illustrates the 3-Tier System Architecture of NK Automobiles. "
        "At the top is Tier 1, the Presentation Layer: Users interact via responsive web pages styled with Bootstrap 5 and accelerated by JavaScript event listeners. "
        "In the middle is Tier 2, the Application Layer: Our Python Flask application handles routing, authentication checks, business logic for compatibility filtering, and dynamic UPI QR generation. "
        "At the bottom is Tier 3, the Database Layer: MySQL 8.0 manages data persistence through 14 normalized tables, accessed via our dedicated db_queries.py interface using parameterized queries."
    )

    # ==========================================
    # SLIDE 8: SYSTEM MODULES (Implemented Features)
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Implemented System Modules", "Functional Decomposition")

    modules = [
        ("1. Product Catalog & Inventory", [
            ("Scope", "181 active automobile spare parts across 8 categories."),
            ("Features", "Search by part name, brand, part number; category filtering; price range slider; real-time stock levels."),
            ("Image Assets", "159 verified real-world component photographs.")
        ]),
        ("2. Two-Wheeler Fitment Engine", [
            ("Compatibility Matrix", "1,655 verified relations covering 11 Indian motorcycle and scooter platforms."),
            ("Live Client Search", "Instant search bar on product page filtering models in real time."),
            ("Badges", "Clear status indicators: Verified Fit, Universal Fit, Confirm Year/BS.")
        ]),
        ("3. Customer Authentication & Portal", [
            ("User Security", "Secure registration and login with encrypted password storage."),
            ("Account Hub", "Customer profile dashboard, order history, tracking status, and personal wishlist toggle."),
            ("Role Security", "Strict separation between regular customers and store admins.")
        ]),
        ("4. Cart & Dynamic Checkout", [
            ("Cart Management", "Real-time quantity modification, price computation, and empty cart handling."),
            ("Coupon Engine", "Discount coupon validation (e.g. FESTIVE10) with automatic order total deduction."),
            ("Guest Checkout", "Enables quick orders with recipient name, phone, and delivery address.")
        ]),
        ("5. UPI QR Payment Workflow", [
            ("Dynamic QR", "Generates order-specific UPI payment QR codes (Google Pay, PhonePe, Paytm)."),
            ("Payment Verification", "Captures customer UTR transaction number for counter reconciliation."),
            ("Receipt Screen", "Instant order confirmation summary with itemized breakdown.")
        ]),
        ("6. Administrative Control Hub", [
            ("Inventory CRUD", "Add, edit, restock, or deactivate spare parts in the catalog."),
            ("Order Manager", "Update fulfillment status: Pending -> Confirmed -> Shipped -> Delivered."),
            ("Audit Logging", "Automated system_logs capturing critical administrative events.")
        ])
    ]

    for i, (m_title, items) in enumerate(modules):
        col = i % 3
        row = i // 3
        mx = 0.8 + (col * 4.0)
        my = 1.5 + (row * 2.8)
        
        add_card(s8, mx, my, 3.733, 2.65, m_title, bg_color=COLOR_WHITE)
        add_bullet_list(s8, mx + 0.2, my + 0.6, 3.333, 1.9, items, font_size=10)

    set_speaker_notes(s8,
        "On Slide 8, we outline the six functional modules implemented in NK Automobiles. "
        "Module 1 handles the 181-part catalog with real-time stock tracking. "
        "Module 2 is our standout feature: the Two-Wheeler Compatibility Engine mapping parts to 11 Indian motorcycle models with instant client-side search. "
        "Module 3 manages secure customer authentication and personal profiles. "
        "Module 4 provides cart management with a coupon engine and guest checkout. "
        "Module 5 generates dynamic UPI QR codes for seamless mobile payments. "
        "Module 6 is the Admin Hub, allowing store managers to perform CRUD operations on inventory, fulfill orders, and monitor audit logs."
    )

    # ==========================================
    # SLIDE 9: DATABASE DESIGN & ER SCHEMA
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Database Design & Entity Relationship (ER) Schema", "Data Architecture")

    # Group 1: Catalog
    add_card(s9, 0.8, 1.5, 3.7, 5.4, "Catalog & Fitment Entities", bg_color=COLOR_WHITE)
    add_bullet_list(s9, 1.05, 2.1, 3.2, 4.5, [
        ("categories", "PK: category_id\nFields: name, description\nStores 8 automotive categories."),
        ("products", "PK: product_id\nFK: category_id -> categories\nFields: name, brand, part_number, price, stock_quantity, image_url, is_active."),
        ("product_compatibility", "PK: compatibility_id\nFK: product_id -> products\nFields: vehicle_model, fitment_status, notes\nMaintains 1,655 verified relations.")
    ], font_size=10.5)

    # Group 2: Orders & Cart
    add_card(s9, 4.8, 1.5, 3.7, 5.4, "Orders & Commerce Entities", bg_color=COLOR_WHITE)
    add_bullet_list(s9, 5.05, 2.1, 3.2, 4.5, [
        ("orders", "PK: order_id\nFK: user_id (NULL for guest)\nFields: total_amount, payment_status, payment_method, order_status, shipping_address, created_at."),
        ("order_items", "PK: item_id\nFK: order_id -> orders\nFK: product_id -> products\nFields: quantity, unit_price, subtotal."),
        ("cart", "PK: cart_id\nFK: user_id, product_id\nFields: quantity, added_at."),
        ("coupons", "PK: coupon_id\nFields: code, discount_percent, is_active.")
    ], font_size=10.5)

    # Group 3: Users & Support
    add_card(s9, 8.8, 1.5, 3.7, 5.4, "User & Audit Entities", bg_color=COLOR_WHITE)
    add_bullet_list(s9, 9.05, 2.1, 3.2, 4.5, [
        ("users", "PK: user_id\nFields: name, email, password_hash, role (admin/customer), phone, created_at."),
        ("wishlist", "PK: wishlist_id\nFK: user_id, product_id\nPersonal saved items."),
        ("reviews & review_media", "Customer ratings & uploaded repair photos."),
        ("contact_messages", "Customer inquiries and fitment consultation queries."),
        ("system_logs", "PK: log_id\nFields: action, user, timestamp, details.")
    ], font_size=10.5)

    set_speaker_notes(s9,
        "Slide 9 demonstrates our relational database design. The system is normalized up to Third Normal Form (3NF) across 14 tables to eliminate data redundancy. "
        "The catalog group links categories to products via a one-to-many relationship, and products to compatibility records via a one-to-many relationship. "
        "The orders group captures e-commerce transactions: an order contains multiple order_items linked to products, preserving historical unit prices at the time of purchase. "
        "The user group handles role-based credentials, customer wishlists, and system audit logs."
    )

    # ==========================================
    # SLIDE 10: CRUD OPERATIONS IN ACTION
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "CRUD Operations in Automobile Inventory Management", "Core Operations")

    crud_data = [
        ("CREATE (Insert Record)", [
            ("Admin Inventory", "Adding a new spare part into the catalog with part number, brand, price, and category."),
            ("Customer Order", "Inserting a new order header into 'orders' and line items into 'order_items'."),
            ("SQL Implementation", "INSERT INTO products (name, category_id, brand, price, stock_quantity) VALUES (%s, %s, %s, %s, %s);")
        ]),
        ("READ (Query & Filter)", [
            ("Vehicle Filter", "Fetching parts compatible with a user's bike (e.g. Hero Splendor Plus or Bajaj Pulsar)."),
            ("Catalog Search", "Multi-parameter filtering by search keyword, category, price range, and in-stock status."),
            ("SQL Implementation", "SELECT p.* FROM products p JOIN product_compatibility pc ON p.product_id = pc.product_id WHERE pc.vehicle_model = %s;")
        ]),
        ("UPDATE (Modify Record)", [
            ("Stock Adjustment", "Decrementing available stock_quantity upon completed order placement."),
            ("Order Status", "Admin advancing fulfillment: Pending -> Confirmed -> Shipped -> Delivered."),
            ("SQL Implementation", "UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s AND stock_quantity >= %s;")
        ]),
        ("DELETE (Soft Deactivation)", [
            ("Integrity Protection", "Physical DELETE cascades can break historical sales records and financial reports."),
            ("Soft Delete Approach", "We implement soft deletion by toggling 'is_active = 0', hiding it from catalog while preserving order history."),
            ("SQL Implementation", "UPDATE products SET is_active = 0 WHERE product_id = %s;")
        ])
    ]

    for i, (c_title, items) in enumerate(crud_data):
        cx = 0.8 + ((i % 2) * 6.0)
        cy = 1.5 + ((i // 2) * 2.8)
        add_card(s10, cx, cy, 5.7, 2.65, c_title, bg_color=COLOR_WHITE)
        add_bullet_list(s10, cx + 0.25, cy + 0.6, 5.2, 1.9, items, font_size=10.5)

    set_speaker_notes(s10,
        "Slide 10 details how fundamental CRUD operations are executed within NK Automobiles using practical automobile examples. "
        "Create is demonstrated when an admin inserts a new spare part or a customer generates an order. "
        "Read powers our catalog and compatibility engine, joining products with product_compatibility based on the user's selected bike model. "
        "Update handles inventory stock decrement and order status fulfillment. "
        "For Delete, we deliberately adopted an industry-standard Soft Delete design: instead of deleting product rows which would corrupt historical invoice records, "
        "we toggle an is_active flag to zero, preserving full relational integrity."
    )

    # ==========================================
    # SLIDE 11: USER INTERFACE DESIGN
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "User Interface Design & User Experience (UX)", "Interface Design")

    ui_cards = [
        ("1. Home & Hero Banner", "High-contrast automobile styling with immediate keyword search bar, popular brand showcases, and category shortcut tiles."),
        ("2. Catalog & Vehicle Filter Sidebar", "Clean multi-faceted filter: category checklist, 11-model vehicle radio selector, and interactive price range slider."),
        ("3. Product Detail & Fitment Guide", "Displays high-res product photo, OEM specs, price, and our interactive live Two-Wheeler Compatibility Table with instant search."),
        ("4. Cart & Dynamic UPI QR Screen", "Itemized cart breakdown, coupon input box, and dynamic UPI QR code generator enabling mobile scan-to-pay."),
        ("5. Guest Checkout Modal", "Streamlined 1-step checkout capturing delivery address and phone number without requiring lengthy account creation."),
        ("6. Admin Operations Dashboard", "Tabular inventory overview, quick stock editor, order fulfillment dropdowns, and recent customer inquiry viewer.")
    ]

    for i, (ui_title, ui_desc) in enumerate(ui_cards):
        col = i % 3
        row = i // 3
        ux = 0.8 + (col * 4.0)
        uy = 1.5 + (row * 2.8)
        
        c = add_card(s11, ux, uy, 3.733, 2.65, ui_title, bg_color=COLOR_WHITE)
        tx = s11.shapes.add_textbox(Inches(ux + 0.25), Inches(uy + 0.65), Inches(3.233), Inches(1.85))
        tf = tx.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = ui_desc
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_TEXT_DARK
        
        # Placeholder indicator
        p2 = tf.add_paragraph()
        p2.text = "[ Screenshot: " + ui_title.split(". ")[1] + " ]"
        p2.font.size = Pt(9.5)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_ACCENT_BLUE
        p2.space_before = Pt(10)

    set_speaker_notes(s11,
        "Slide 11 highlights the user interface design. We engineered the UI following mobile-first responsive design principles using Bootstrap 5. "
        "The customer experience is centered on convenience: users can search by part name or filter by bike model from the sidebar. "
        "On the product details page, our vehicle compatibility widget provides instant client-side bike searching without reloading the page. "
        "The checkout interface features guest ordering and an integrated UPI QR code, while the admin dashboard provides intuitive inventory management."
    )

    # ==========================================
    # SLIDE 12: SYSTEM WORKFLOW & REQUEST CYCLE
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "System Workflow & Request-Response Lifecycle", "Data Flow")

    workflow_steps = [
        ("Step 1: User Request", "Client interacts with browser (e.g. filters by 'Hero Splendor Plus' or submits an order). An HTTP GET/POST request is dispatched to the Flask server."),
        ("Step 2: Routing & Middleware", "Flask WSGI server inspects the URL route (@app.route('/products')), executes session security checks, and extracts query parameters."),
        ("Step 3: Controller & Business Logic", "The controller calls db_queries methods. For fitment queries, it validates model parameters and prepares the SQL statement."),
        ("Step 4: MySQL Query Execution", "The database connector opens a connection from the pool, executes parameterized SQL with bound parameters, and retrieves record tuples."),
        ("Step 5: Jinja2 Template Rendering", "Flask merges the database recordsets with HTML templates (e.g. products.html), injecting stock counts, prices, and fitment badges."),
        ("Step 6: Client DOM Update", "The browser receives semantic HTML/CSS and initializes JavaScript event listeners for live searching and quantity updates.")
    ]

    for i, (w_title, w_desc) in enumerate(workflow_steps):
        wy = 1.5 + (i * 0.9)
        c = add_card(s12, 0.8, wy, 11.733, 0.82, bg_color=COLOR_WHITE)
        
        # Step label
        lbl = s12.shapes.add_textbox(Inches(1.0), Inches(wy + 0.12), Inches(3.2), Inches(0.55))
        tf_l = lbl.text_frame
        p_l = tf_l.paragraphs[0]
        p_l.text = w_title
        p_l.font.bold = True
        p_l.font.size = Pt(12)
        p_l.font.color.rgb = COLOR_NAVY_DARK
        
        # Step desc
        desc_box = s12.shapes.add_textbox(Inches(4.3), Inches(wy + 0.12), Inches(8.0), Inches(0.55))
        tf_d = desc_box.text_frame
        tf_d.word_wrap = True
        p_d = tf_d.paragraphs[0]
        p_d.text = w_desc
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = COLOR_TEXT_MUTED

    set_speaker_notes(s12,
        "Slide 12 walks through the internal system workflow and execution lifecycle for an HTTP request. "
        "When a user selects a bike filter or submits an order, the browser dispatches an HTTP request. "
        "Flask routes the request through session middleware, calls our data access layer in db_queries.py, and executes a parameterized SQL query on MySQL. "
        "The returned records are processed and handed to Jinja2, which compiles the HTML template and returns it to the client browser in milliseconds."
    )

    # ==========================================
    # SLIDE 13: SOFTWARE TESTING & RESULTS
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "Software Testing, Test Cases & Verification Results", "Quality Assurance")

    # Table layout
    rows, cols = 7, 5
    left, top, width, height = Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.4)
    table_shape = s13.shapes.add_table(rows, cols, left, top, width, height)
    tbl = table_shape.table

    tbl.columns[0].width = Inches(1.1)
    tbl.columns[1].width = Inches(2.7)
    tbl.columns[2].width = Inches(3.6)
    tbl.columns[3].width = Inches(3.433)
    tbl.columns[4].width = Inches(0.9)

    test_cases = [
        ("TC ID", "Module Tested", "Test Description & Input", "Expected & Actual Outcome", "Result"),
        ("TC-01", "Fitment Engine", "Filter catalog by vehicle model 'Hero Splendor Plus'.", "Returns 164 compatible parts; completely excludes scooter CVT filters & clutch cables.", "PASS"),
        ("TC-02", "Authentication", "Attempt unauthorized access to /admin without admin session.", "Flask session validator halts request and redirects to login with flash warning.", "PASS"),
        ("TC-03", "Cart & Coupon", "Apply coupon code 'FESTIVE10' on cart subtotal of ₹1,000.", "Applies 10% discount (₹100); recalculates total to ₹900 accurately.", "PASS"),
        ("TC-04", "Guest Checkout", "Submit order with name, phone, and address without login.", "Order created in database with user_id=NULL; unique order ID generated.", "PASS"),
        ("TC-05", "Live Bike Filter", "Type 'Pulsar' into live compatibility search bar on /product/24.", "Instantly isolates Pulsar 150 & NS200 rows; hides non-matching models in DOM.", "PASS"),
        ("TC-06", "Inventory Update", "Complete checkout for 2 units of item with stock_quantity=10.", "Atomic transaction completes; stock_quantity correctly decremented to 8 in MySQL.", "PASS")
    ]

    for r_idx, row in enumerate(test_cases):
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.text = val
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.font.name = "Calibri"
            
            if r_idx == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_NAVY_DARK
                p.font.bold = True
                p.font.size = Pt(11)
                p.font.color.rgb = COLOR_WHITE
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_WHITE if r_idx % 2 == 1 else RGBColor(248, 250, 252)
                p.font.size = Pt(9.5)
                p.font.color.rgb = COLOR_TEXT_DARK
                if c_idx == 0:
                    p.font.bold = True
                elif c_idx == 4:
                    p.font.bold = True
                    p.font.color.rgb = COLOR_SUCCESS
                    p.alignment = PP_ALIGN.CENTER

    set_speaker_notes(s13,
        "Slide 13 summarizes our software testing methodology and verification results. "
        "We tested all major functional modules using a combination of automated Python unittest test suites and manual validation. "
        "Test Case 1 verified our Two-Wheeler Compatibility Engine: selecting Hero Splendor Plus successfully returned compatible parts while strictly excluding scooter CVT components. "
        "Test Case 2 validated security by verifying that unauthenticated users cannot access administrative endpoints. "
        "Other test cases verified coupon calculations, guest checkout, instant DOM filtering, and transactional stock deductions—all achieving 100% pass rates."
    )

    # ==========================================
    # SLIDE 14: ADVANTAGES & LIMITATIONS
    # ==========================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_header(s14, "Practical Advantages & Current System Limitations", "System Evaluation")

    add_card(s14, 0.8, 1.5, 5.7, 5.4, "Practical Advantages", bg_color=COLOR_WHITE)
    add_bullet_list(s14, 1.05, 2.1, 5.2, 4.5, [
        ("Zero Part-Mismatch Returns", "The verified two-wheeler compatibility engine eliminates customer confusion and dramatically reduces product return costs."),
        ("Frictionless Sales Conversion", "Guest checkout allows customers and local mechanics to complete purchases in seconds without password hurdles."),
        ("High-Performance Lightweight Stack", "Python Flask delivers lightning-fast page response times compared to heavy enterprise frameworks."),
        ("ACID-Compliant Transactions", "MySQL ensures consistent inventory numbers and prevents phantom reads or duplicate order anomalies."),
        ("Responsive Cross-Platform UI", "Optimized for mechanics ordering via Android smartphones or desktop counter staff.")
    ], font_size=11)

    add_card(s14, 6.8, 1.5, 5.7, 5.4, "Current Limitations", bg_color=COLOR_WHITE)
    add_bullet_list(s14, 7.05, 2.1, 5.2, 4.5, [
        ("Manual Payment Reconciliation", "UPI payments rely on customer UTR transaction entry rather than an automated bank webhook settlement gateway."),
        ("Offline Barcode POS Integration", "The current web app does not yet interface with physical counter handheld laser barcode scanners."),
        ("Single-Currency Scope", "Transactions and pricing are restricted to Indian Rupees (INR) for domestic automobile retail."),
        ("Manual Stock Refill Trigger", "Store managers must periodically check stock reports rather than receiving automated supplier purchase orders."),
        ("Local Delivery Radius", "Shipping calculations currently assume local Hubballi and regional Karnataka fulfillment.")
    ], font_size=11)

    set_speaker_notes(s14,
        "On Slide 14, we present a balanced academic evaluation of our system. "
        "The primary advantage is our fitment engine, which directly addresses the biggest operational problem in automobile parts retail: incompatible orders. "
        "Furthermore, guest checkout and responsive design maximize sales conversion. "
        "In terms of limitations, our UPI payment currently relies on customer UTR entry rather than a bank gateway webhook, "
        "and physical counter barcode scanner integration is not yet connected to the web database. These boundaries form the foundation of our future enhancements."
    )

    # ==========================================
    # SLIDE 15: FUTURE ENHANCEMENTS
    # ==========================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15)
    add_header(s15, "Proposed Future Enhancements", "Project Roadmap")

    enhancements = [
        ("1. Payment Gateway Webhook Integration", "Integrate automated Razorpay or Cashfree webhooks to achieve instantaneous, zero-human-touch UPI payment confirmation and invoice clearing."),
        ("2. Automated WhatsApp & SMS Notifications", "Connect Twilio / Gupshup WhatsApp APIs to send instant order confirmations, dispatched courier tracking links, and pickup OTPs to customers."),
        ("3. Automated PDF Tax Invoice Generation", "Implement ReportLab / WeasyPrint to auto-generate downloadable, GST-compliant tax invoices with shop registration numbers upon order completion."),
        ("4. Predictive Low-Stock Supplier Alerts", "Establish automated background cron jobs that detect when fast-moving items drop below threshold and auto-draft supplier purchase orders."),
        ("5. Machine Learning Part Recommendations", "Deploy an association-rule recommendation engine suggesting complementary spares during checkout (e.g. suggesting brake fluid when purchasing disc pads).")
    ]

    for i, (f_title, f_desc) in enumerate(enhancements):
        fy = 1.5 + (i * 1.08)
        c = add_card(s15, 0.8, fy, 11.733, 0.95, bg_color=COLOR_WHITE)
        
        # Icon / Badge
        b_box = s15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(fy + 0.18), Inches(0.6), Inches(0.58))
        b_box.fill.solid()
        b_box.fill.fore_color.rgb = COLOR_NAVY_MID
        b_box.line.fill.background()
        tf_b = b_box.text_frame
        p_b = tf_b.paragraphs[0]
        p_b.text = f"F{i+1}"
        p_b.font.size = Pt(12)
        p_b.font.bold = True
        p_b.font.color.rgb = COLOR_WHITE
        p_b.alignment = PP_ALIGN.CENTER
        
        # Text
        tx = s15.shapes.add_textbox(Inches(1.8), Inches(fy + 0.15), Inches(10.5), Inches(0.65))
        tf = tx.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = f_title
        p1.font.bold = True
        p1.font.size = Pt(12.5)
        p1.font.color.rgb = COLOR_NAVY_DARK
        p2 = tf.add_paragraph()
        p2.text = f_desc
        p2.font.size = Pt(10)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(2)

    set_speaker_notes(s15,
        "Slide 15 highlights our future enhancement roadmap. In subsequent releases, we plan to implement automated Razorpay payment webhooks for instantaneous settlement. "
        "Second, we aim to integrate WhatsApp messaging for real-time order tracking updates. "
        "Third, add automated GST-compliant PDF invoice generation. "
        "Fourth, introduce automated supplier re-ordering triggers when stock drops below minimum safety thresholds. "
        "Fifth, implement a machine learning recommendation system to suggest complementary maintenance parts during checkout."
    )

    # ==========================================
    # SLIDE 16: CONCLUSION & ACKNOWLEDGEMENTS
    # ==========================================
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_background(s16)
    add_header(s16, "Conclusion & MCA Learning Outcomes", "Project Conclusion")

    add_card(s16, 0.8, 1.5, 5.7, 5.4, "Project Conclusion & Impact", bg_color=COLOR_WHITE)
    add_bullet_list(s16, 1.05, 2.1, 5.2, 4.5, [
        ("Successful Digitalization", "NK Automobiles successfully bridges traditional retail automobile shopkeeping with modern, scalable web engineering."),
        ("Solves Core Industry Pain", "The Two-Wheeler Compatibility Engine sets this system apart by eliminating part mismatch returns across 1,655 vehicle relations."),
        ("Commercial Readiness", "Features like Guest Checkout and dynamic UPI QR codes make the application instantly deployable for real-world business."),
        ("Clean Maintainable Codebase", "Built with clean MVC separation, parameterized SQL security, and modular Python Flask architecture.")
    ], font_size=11)

    add_card(s16, 6.8, 1.5, 5.7, 5.4, "MCA Technical Learning Outcomes", bg_color=COLOR_WHITE)
    add_bullet_list(s16, 7.05, 2.1, 5.2, 4.5, [
        ("Full-Stack MVC Mastery", "Gained deep practical expertise connecting Python Flask controllers with dynamic Jinja2 templates and relational databases."),
        ("Relational Database Optimization", "Designed a 14-table 3NF schema executing ACID-safe transactions, indexing, and foreign key constraints."),
        ("Application Security", "Implemented password encryption (Werkzeug), role-based authorization, and SQL injection prevention."),
        ("Test-Driven Engineering", "Practiced automated test suite verification using Python unittest and live browser validation.")
    ], font_size=11)

    # Bottom Acknowledgement banner
    b_banner = s16.shapes.add_textbox(Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.8))
    tf_bb = b_banner.text_frame
    p_bb = tf_bb.paragraphs[0]
    p_bb.text = "Thank you to our Project Guide, HOD, Faculty of Chetan Business School, and External Examiners. We welcome your questions!"
    p_bb.font.size = Pt(11.5)
    p_bb.font.bold = True
    p_bb.font.color.rgb = COLOR_NAVY_DARK
    p_bb.alignment = PP_ALIGN.CENTER

    set_speaker_notes(s16,
        "In conclusion, the NK Automobiles project demonstrates how thoughtful software engineering can solve genuine industry bottlenecks. "
        "Through this project, we mastered full-stack Python Flask web architecture, normalized relational database design, and web security principles. "
        "We express our sincere gratitude to our project guide, the faculty of Chetan Business School, and our examiners. "
        "We are now ready for your questions and viva discussion. Thank you!"
    )

    # ==========================================
    # SLIDE 17: APPENDIX - VIVA VOCE QUESTIONS & ANSWERS
    # ==========================================
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_background(s17)
    add_header(s17, "Appendix: Top 10 MCA Viva Voce Questions & Model Answers", "Viva Preparation")

    viva_qas = [
        ("Q1: Why did you choose Flask over Django?", "Flask is a lightweight micro-framework giving full architectural control without the monolithic overhead of Django, making it ideal for custom automotive schemas and fast execution."),
        ("Q2: How do you prevent SQL Injection?", "Every database interaction in db_queries.py uses parameterized queries (e.g. cursor.execute(query, tuple(params))) where user inputs are treated as literal values, never concatenated."),
        ("Q3: How is password security managed?", "Passwords are never stored in plaintext. We utilize Werkzeug Security's generate_password_hash() and check_password_hash(), utilizing salted cryptographic hashing."),
        ("Q4: What is the normalization level of your schema?", "The database is normalized to Third Normal Form (3NF). Repeating groups are eliminated, partial dependencies are removed, and transitive dependencies are decoupled into separate tables."),
        ("Q5: How does the Two-Wheeler Compatibility Engine work?", "It uses a many-to-many relationship table (product_compatibility) linking products to specific bike models. A client-side JavaScript engine provides instant real-time filtering without page reloads."),
        ("Q6: How are database transactions handled during order checkout?", "We wrap order creation and stock decrement in an atomic transaction: if any insertion fails, conn.rollback() triggers, preventing phantom orders or corrupted stock counts."),
        ("Q7: Why implement Guest Checkout?", "Automobile customers often need quick emergency spares and abandon purchases if forced to register. Guest checkout maximizes conversion by requiring only recipient details."),
        ("Q8: How does the dynamic UPI QR code function?", "It dynamically encodes standard NPCI UPI URI strings containing the payee VPA, payee name, amount, and order reference ID into a scannable QR code."),
        ("Q9: What happens if an admin tries to delete a product already present in previous orders?", "We implemented Soft Deletion (setting is_active = 0). Physical deletion is avoided to protect referential integrity and historical financial reports."),
        ("Q10: How are user sessions handled in Flask?", "Sessions are cryptographically signed using Flask's SECRET_KEY and stored in secure browser cookies, preventing client-side tampering of user IDs and admin roles.")
    ]

    for i, (q, a) in enumerate(viva_qas):
        col = i % 2
        row = i // 2
        qx = 0.8 + (col * 6.0)
        qy = 1.5 + (row * 1.1)
        
        c = add_card(s17, qx, qy, 5.7, 1.0, bg_color=COLOR_WHITE)
        tx = s17.shapes.add_textbox(Inches(qx + 0.15), Inches(qy + 0.1), Inches(5.4), Inches(0.8))
        tf = tx.text_frame
        tf.word_wrap = True
        
        p_q = tf.paragraphs[0]
        p_q.text = q
        p_q.font.bold = True
        p_q.font.size = Pt(10)
        p_q.font.color.rgb = COLOR_NAVY_DARK
        
        p_a = tf.add_paragraph()
        p_a.text = a
        p_a.font.size = Pt(9)
        p_a.font.color.rgb = COLOR_TEXT_MUTED
        p_a.space_before = Pt(2)

    set_speaker_notes(s17,
        "This slide serves as an executive reference for the top 10 technical questions examiners frequently ask during an MCA project viva voce. "
        "It covers framework justification, security, SQL injection protection, 3NF normalization, atomic transaction management, and session architecture."
    )

    prs.save(output_path)
    print(f"[SUCCESS] Presentation generated successfully with {len(prs.slides)} slides at: {output_path}")

if __name__ == '__main__':
    create_presentation()

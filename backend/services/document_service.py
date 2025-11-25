"""
Document generation service.
Handles creation and editing of legal documents with PDF generation.
"""
import re
from io import BytesIO
from typing import Dict, Tuple, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors


class DocumentService:
    """Service for generating and editing legal documents."""

    @staticmethod
    def _create_pdf(content_blocks: list, title: str = "Legal Document") -> bytes:
        """
        Create a PDF from content blocks.

        Args:
            content_blocks: List of tuples (text, style_name) where style_name is
                          'title', 'heading', 'normal', 'bullet', or 'signature'
            title: Document title for metadata

        Returns:
            PDF as bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        # Define styles
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leading=14
        )

        bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            leftIndent=20,
            spaceAfter=6,
            leading=14
        )

        signature_style = ParagraphStyle(
            'CustomSignature',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            leading=14
        )

        style_map = {
            'title': title_style,
            'heading': heading_style,
            'normal': normal_style,
            'bullet': bullet_style,
            'signature': signature_style
        }

        # Build story
        story = []
        for block in content_blocks:
            text = block[0]
            style_name = block[1]
            highlight = False
            if len(block) > 2:
                highlight = block[2]
            
            style = style_map.get(style_name, normal_style)
            
            if highlight:
                # Create a highlighted version of the style
                style = ParagraphStyle(
                    f'Highlighted{style_name}',
                    parent=style,
                    backColor=colors.yellow
                )
            
            story.append(Paragraph(text, style))
            if style_name in ['title', 'heading']:
                story.append(Spacer(1, 0.2 * inch))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    @staticmethod
    def generate_director_appointment(data: Dict, highlight_field: str = None) -> Tuple[bytes, Dict]:
        """
        Generate a director appointment resolution as PDF.

        Args:
            data: Dictionary containing director information
                - director_name: Name of the director
                - effective_date: Date of appointment
                - committees: Committees to join (optional)
                - resolution_number: Resolution number (optional)
            highlight_field: Optional field name to highlight

        Returns:
            Tuple of (PDF bytes, document data dictionary)
        """
        name = data.get('director_name', '[DIRECTOR NAME]')
        effective_date = data.get('effective_date', '[EFFECTIVE DATE]')
        committees = data.get('committees', '')
        resolution_number = data.get('resolution_number', 'RES-2024-001')

        committee_text = f" and appointed to the {committees}" if committees else ""

        # Store structured data for editing
        doc_data = {
            'type': 'director_appointment',
            'director_name': name,
            'effective_date': effective_date,
            'committees': committees,
            'resolution_number': resolution_number
        }

        content_blocks = [
            ("BOARD RESOLUTION", 'title'),
            ("APPOINTMENT OF DIRECTOR", 'title'),
            ("", 'normal'),
            (f"Resolution Number: {resolution_number}", 'normal'),
            (f"Date: {effective_date}", 'normal'),
            ("", 'normal'),
            ("RESOLVED THAT:", 'heading'),
            ("", 'normal'),
            ("1. APPOINTMENT", 'heading'),
            (f"{name} is hereby appointed as a Director of the Company, effective {effective_date}.", 'normal'),
            ("", 'normal'),
            ("2. AUTHORITY", 'heading'),
            ("The Director shall have all rights, powers, and responsibilities as set forth in the Company's Articles of Incorporation and Bylaws.", 'normal'),
            ("", 'normal'),
            ("3. COMMITTEE ASSIGNMENTS", 'heading'),
            (f"{name} is{committee_text if committee_text else ' not assigned to any committees at this time'}.", 'normal'),
            ("", 'normal'),
            ("4. EFFECTIVE DATE", 'heading'),
            (f"This resolution shall be effective as of {effective_date}.", 'normal'),
            ("", 'normal'),
            ("5. CERTIFICATION", 'heading'),
            ("The undersigned Secretary certifies that the foregoing resolution was duly adopted by the Board of Directors and remains in full force and effect.", 'normal'),
            ("", 'normal'),
            (f"Executed this day: {effective_date}", 'normal'),
            ("", 'normal'),
            ("_________________________________", 'signature'),
            ("Corporate Secretary", 'signature'),
            ("", 'normal'),
            ("_________________________________", 'signature'),
            ("Board Chairperson", 'signature'),
        ]

        pdf_bytes = DocumentService._create_pdf(content_blocks, "Director Appointment Resolution")
        return pdf_bytes, doc_data

    @staticmethod
    def generate_nda(data: Dict, highlight_field: str = None) -> Tuple[bytes, Dict]:
        """
        Generate a Non-Disclosure Agreement as PDF.

        Args:
            data: Dictionary containing NDA information
                - party1_name: First party name
                - party2_name: Second party name
                - effective_date: Effective date
                - term_years: Term in years (optional)
            highlight_field: Optional field name to highlight

        Returns:
            Tuple of (PDF bytes, document data dictionary)
        """
        party1 = data.get('party1_name', '[PARTY 1 NAME]')
        party2 = data.get('party2_name', '[PARTY 2 NAME]')
        effective_date = data.get('effective_date', '[EFFECTIVE DATE]')
        term_years = data.get('term_years', '2')

        # Store structured data for editing
        doc_data = {
            'type': 'nda',
            'party1_name': party1,
            'party2_name': party2,
            'effective_date': effective_date,
            'term_years': term_years
        }

        content_blocks = [
            ("NON-DISCLOSURE AGREEMENT", 'title'),
            ("", 'normal'),
            (f'This Non-Disclosure Agreement ("Agreement") is entered into as of {effective_date} ("Effective Date")', 'normal', highlight_field == 'effective_date'),
            ("", 'normal'),
            ("BETWEEN:", 'heading'),
            (f'{party1} ("Disclosing Party")', 'normal', highlight_field == 'party1_name'),
            ("", 'normal'),
            ("AND:", 'heading'),
            (f'{party2} ("Receiving Party")', 'normal', highlight_field == 'party2_name'),
            ("", 'normal'),
            ("WHEREAS the Disclosing Party possesses certain confidential and proprietary information; and", 'normal'),
            ("", 'normal'),
            ("WHEREAS the Receiving Party desires to receive such confidential information for legitimate business purposes;", 'normal'),
            ("", 'normal'),
            ("NOW THEREFORE, in consideration of the mutual covenants and agreements contained herein, the parties agree as follows:", 'normal'),
            ("", 'normal'),
            ("1. DEFINITION OF CONFIDENTIAL INFORMATION", 'heading'),
            ('"Confidential Information" means any and all technical and non-technical information disclosed by the Disclosing Party, including but not limited to: trade secrets, business strategies, customer lists, financial information, product designs, software, and any other proprietary information.', 'normal'),
            ("", 'normal'),
            ("2. OBLIGATIONS OF RECEIVING PARTY", 'heading'),
            ("The Receiving Party agrees to:", 'normal'),
            ("a) Hold all Confidential Information in strict confidence", 'bullet'),
            ("b) Not disclose Confidential Information to any third party without prior written consent", 'bullet'),
            ("c) Use Confidential Information solely for the agreed business purpose", 'bullet'),
            ("d) Protect Confidential Information with the same degree of care used for its own confidential information", 'bullet'),
            ("", 'normal'),
            ("3. TERM", 'heading'),
            (f"This Agreement shall remain in effect for {term_years} years from the Effective Date. The obligations regarding Confidential Information shall survive termination for an additional {term_years} years.", 'normal'),
            ("", 'normal'),
            ("4. RETURN OF MATERIALS", 'heading'),
            ("Upon termination or upon request, the Receiving Party shall return or destroy all Confidential Information and certify such destruction in writing.", 'normal'),
            ("", 'normal'),
            ("5. NO LICENSE", 'heading'),
            ("Nothing in this Agreement grants any license or right to the Receiving Party regarding intellectual property of the Disclosing Party.", 'normal'),
            ("", 'normal'),
            ("6. GOVERNING LAW", 'heading'),
            ("This Agreement shall be governed by the laws of the applicable jurisdiction.", 'normal'),
            ("", 'normal'),
            ("IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.", 'normal'),
            ("", 'normal'),
            ("_________________________________", 'signature'),
            (f"Disclosing Party: {party1}", 'signature', highlight_field == 'party1_name'),
            ("Date: _______________", 'signature'),
            ("", 'normal'),
            ("", 'normal'),
            ("_________________________________", 'signature'),
            (f"Receiving Party: {party2}", 'signature', highlight_field == 'party2_name'),
            ("Date: _______________", 'signature'),
        ]

        pdf_bytes = DocumentService._create_pdf(content_blocks, "Non-Disclosure Agreement")
        return pdf_bytes, doc_data

    @staticmethod
    def generate_employment_agreement(data: Dict, highlight_field: str = None) -> Tuple[bytes, Dict]:
        """
        Generate an Employment Agreement as PDF.

        Args:
            data: Dictionary containing employment information
                - employee_name: Employee name
                - company_name: Company name
                - position: Job position
                - start_date: Start date
                - salary: Annual salary
            highlight_field: Optional field name to highlight

        Returns:
            Tuple of (PDF bytes, document data dictionary)
        """
        employee_name = data.get('employee_name', '[EMPLOYEE NAME]')
        company_name = data.get('company_name', '[COMPANY NAME]')
        position = data.get('position', '[POSITION]')
        start_date = data.get('start_date', '[START DATE]')
        salary = data.get('salary', '[SALARY]')

        # Store structured data for editing
        doc_data = {
            'type': 'employment_agreement',
            'employee_name': employee_name,
            'company_name': company_name,
            'position': position,
            'start_date': start_date,
            'salary': salary
        }

        content_blocks = [
            ("EMPLOYMENT AGREEMENT", 'title'),
            ("", 'normal'),
            (f"This Employment Agreement (\"Agreement\") is entered into as of {start_date}", 'normal', highlight_field == 'start_date'),
            ("", 'normal'),
            ("BETWEEN:", 'heading'),
            (f'{company_name} ("Company")', 'normal', highlight_field == 'company_name'),
            ("", 'normal'),
            ("AND:", 'heading'),
            (f'{employee_name} ("Employee")', 'normal', highlight_field == 'employee_name'),
            ("", 'normal'),
            ("1. POSITION AND DUTIES", 'heading'),
            (f"The Company hereby employs the Employee in the position of {position}. The Employee accepts such employment and agrees to perform all duties and responsibilities associated with this position.", 'normal', highlight_field == 'position'),
            ("", 'normal'),
            ("2. COMPENSATION", 'heading'),
            (f"The Company shall pay the Employee an annual salary of {salary}, payable in accordance with the Company's standard payroll practices.", 'normal', highlight_field == 'salary'),
            ("", 'normal'),
            ("3. START DATE", 'heading'),
            (f"Employment shall commence on {start_date}.", 'normal', highlight_field == 'start_date'),
            ("", 'normal'),
            ("4. EMPLOYMENT RELATIONSHIP", 'heading'),
            ("This is an at-will employment relationship. Either party may terminate this agreement at any time, with or without cause, with or without notice.", 'normal'),
            ("", 'normal'),
            ("5. DUTIES AND RESPONSIBILITIES", 'heading'),
            ("The Employee shall:", 'normal'),
            ("a) Devote their full business time and attention to the performance of their duties", 'bullet'),
            ("b) Comply with all Company policies and procedures", 'bullet'),
            ("c) Act in the best interests of the Company at all times", 'bullet'),
            ("d) Not engage in any competing business activities", 'bullet'),
            ("", 'normal'),
            ("6. CONFIDENTIALITY", 'heading'),
            ("The Employee acknowledges that during employment they will have access to confidential information and trade secrets of the Company. The Employee agrees to maintain strict confidentiality of all such information during and after employment.", 'normal'),
            ("", 'normal'),
            ("7. BENEFITS", 'heading'),
            ("The Employee shall be eligible for benefits in accordance with Company policies, including but not limited to health insurance, paid time off, and retirement plans as applicable.", 'normal'),
            ("", 'normal'),
            ("8. TERMINATION", 'heading'),
            ("Either party may terminate this Agreement with written notice. Upon termination, the Employee shall:", 'normal'),
            ("a) Return all Company property", 'bullet'),
            ("b) Continue to maintain confidentiality obligations", 'bullet'),
            ("c) Receive final compensation for work performed through the termination date", 'bullet'),
            ("", 'normal'),
            ("9. GOVERNING LAW", 'heading'),
            ("This Agreement shall be governed by the laws of the applicable jurisdiction.", 'normal'),
            ("", 'normal'),
            ("IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.", 'normal'),
            ("", 'normal'),
            ("_________________________________", 'signature'),
            (f"Company Representative: {company_name}", 'signature', highlight_field == 'company_name'),
            ("Date: _______________", 'signature'),
            ("", 'normal'),
            ("", 'normal'),
            ("_________________________________", 'signature'),
            (f"Employee: {employee_name}", 'signature', highlight_field == 'employee_name'),
            ("Date: _______________", 'signature'),
        ]

        pdf_bytes = DocumentService._create_pdf(content_blocks, "Employment Agreement")
        return pdf_bytes, doc_data

    @staticmethod
    def generate_custom_document(data: Dict, highlight_field: str = None) -> Tuple[bytes, Dict]:
        """
        Generate a custom document based on provided data.
        This is a flexible method that can handle various custom document types.

        Args:
            data: Dictionary containing document information
                - title: Document title (required)
                - sections: List of sections, each with 'heading' and 'content'
                - date: Document date (optional)
                - parties: List of party names (optional)
                - additional fields as needed
            highlight_field: Optional field name to highlight

        Returns:
            Tuple of (PDF bytes, document data dictionary)
        """
        title = data.get('title', 'LEGAL DOCUMENT')
        sections = data.get('sections', [])
        doc_date = data.get('date', '[DATE]')
        parties = data.get('parties', [])

        # Store structured data for editing
        doc_data = {
            'type': 'custom',
            'title': title,
            'sections': sections,
            'date': doc_date,
            'parties': parties,
            **{k: v for k, v in data.items() if k not in ['title', 'sections', 'date', 'parties']}
        }

        content_blocks = [
            (title.upper(), 'title', highlight_field == 'title'),
            ("", 'normal'),
        ]

        if doc_date:
            content_blocks.append((f"Date: {doc_date}", 'normal', highlight_field == 'date'))
            content_blocks.append(("", 'normal'))

        # Add parties if provided
        if parties:
            content_blocks.append(("PARTIES:", 'heading'))
            content_blocks.append(("", 'normal'))
            for party in parties:
                content_blocks.append((party, 'normal', highlight_field == 'parties'))
            content_blocks.append(("", 'normal'))

        # Add sections
        for i, section in enumerate(sections, 1):
            heading = section.get('heading', f'Section {i}')
            content = section.get('content', '')
            
            # Check if this section is being highlighted (by heading name)
            is_highlighted = highlight_field == heading

            content_blocks.append((f"{i}. {heading.upper()}", 'heading', is_highlighted))

            # Handle content that might be a list or a string
            if isinstance(content, list):
                for item in content:
                    content_blocks.append((item, 'bullet', is_highlighted))
            else:
                content_blocks.append((content, 'normal', is_highlighted))
            content_blocks.append(("", 'normal'))

        # Add signature lines
        content_blocks.extend([
            ("", 'normal'),
            ("_________________________________", 'signature'),
            ("Signature", 'signature'),
            ("", 'normal'),
            ("Date: _______________", 'signature'),
        ])

        pdf_bytes = DocumentService._create_pdf(content_blocks, title)
        return pdf_bytes, doc_data

    @staticmethod
    def apply_edit(
        doc_data: Dict,
        edit_type: str,
        field_name: str,
        new_value: Any
    ) -> Tuple[bytes, bytes, Dict, str]:
        """
        Apply edits to a document and regenerate PDF.

        Args:
            doc_data: Current document data dictionary
            edit_type: Type of edit ('update_field', 'add_section', 'remove_section')
            field_name: Name of field to edit
            new_value: New value to apply

        Returns:
            Tuple of (preview PDF bytes, download PDF bytes, updated doc_data, change_description)
        """
        # Make a copy to avoid modifying the original
        updated_data = doc_data.copy()
        changes = []

        if edit_type == 'update_field':
            # Update a specific field
            if field_name in updated_data:
                old_value = updated_data[field_name]
                updated_data[field_name] = new_value
                changes.append(f"Updated {field_name} from '{old_value}' to '{new_value}'")
            else:
                # Add new field if it doesn't exist
                updated_data[field_name] = new_value
                changes.append(f"Added {field_name}: '{new_value}'")

        elif edit_type == 'add_section':
            # Add a new section (for custom documents)
            if 'sections' not in updated_data:
                updated_data['sections'] = []
            updated_data['sections'].append({
                'heading': field_name,
                'content': new_value
            })
            changes.append(f"Added section: {field_name}")

        elif edit_type == 'remove_section':
            # Remove a section
            if 'sections' in updated_data:
                updated_data['sections'] = [
                    s for s in updated_data['sections']
                    if s.get('heading') != field_name
                ]
                changes.append(f"Removed section: {field_name}")

        # Regenerate the document based on type
        doc_type = updated_data.get('type', 'custom')

        try:
            # Generate preview with highlights
            if doc_type == 'director_appointment':
                pdf_preview, _ = DocumentService.generate_director_appointment(updated_data, highlight_field=field_name)
                pdf_download, updated_data = DocumentService.generate_director_appointment(updated_data, highlight_field=None)
            elif doc_type == 'nda':
                pdf_preview, _ = DocumentService.generate_nda(updated_data, highlight_field=field_name)
                pdf_download, updated_data = DocumentService.generate_nda(updated_data, highlight_field=None)
            elif doc_type == 'employment_agreement':
                pdf_preview, _ = DocumentService.generate_employment_agreement(updated_data, highlight_field=field_name)
                pdf_download, updated_data = DocumentService.generate_employment_agreement(updated_data, highlight_field=None)
            elif doc_type == 'custom':
                pdf_preview, _ = DocumentService.generate_custom_document(updated_data, highlight_field=field_name)
                pdf_download, updated_data = DocumentService.generate_custom_document(updated_data, highlight_field=None)
            else:
                raise ValueError(f"Unsupported document type: {doc_type}")

            change_description = '; '.join(changes) if changes else f"Updated {field_name}"
            return pdf_preview, pdf_download, updated_data, change_description

        except Exception as e:
            raise ValueError(f"Error regenerating document: {str(e)}")

    @staticmethod
    def generate(document_type: str, document_data: Dict, highlight_field: str = None) -> Tuple[bytes, Dict]:
        """
        Generate a document based on type.

        Args:
            document_type: Type of document to generate
            document_data: Data for document generation
            highlight_field: Optional field name to highlight

        Returns:
            Tuple of (PDF bytes, document data dictionary)

        Raises:
            ValueError: If document type is not supported
        """
        document_type_lower = document_type.lower()

        if 'director' in document_type_lower or 'appointment' in document_type_lower:
            return DocumentService.generate_director_appointment(document_data, highlight_field)
        elif 'nda' in document_type_lower or 'non-disclosure' in document_type_lower:
            return DocumentService.generate_nda(document_data, highlight_field)
        elif 'employment' in document_type_lower:
            return DocumentService.generate_employment_agreement(document_data, highlight_field)
        else:
            # Try to generate a custom document for unknown types
            return DocumentService.generate_custom_document(document_data, highlight_field)

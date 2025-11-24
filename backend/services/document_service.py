"""
Document generation service.
Handles creation and editing of legal documents.
"""
import re
from typing import Dict, Tuple


class DocumentService:
    """Service for generating and editing legal documents."""

    @staticmethod
    def generate_director_appointment(data: Dict) -> str:
        """
        Generate a director appointment resolution.

        Args:
            data: Dictionary containing director information
                - director_name: Name of the director
                - effective_date: Date of appointment
                - committees: Committees to join (optional)
                - resolution_number: Resolution number (optional)

        Returns:
            Formatted director appointment document
        """
        name = data.get('director_name', '[DIRECTOR NAME]')
        effective_date = data.get('effective_date', '[EFFECTIVE DATE]')
        committees = data.get('committees', '')
        resolution_number = data.get('resolution_number', 'RES-2024-001')

        committee_text = f" and appointed to the {committees}" if committees else ""

        document = f"""
BOARD RESOLUTION
APPOINTMENT OF DIRECTOR

Resolution Number: {resolution_number}
Date: {effective_date}

RESOLVED THAT:

1. APPOINTMENT
   {name} is hereby appointed as a Director of the Company, effective {effective_date}.

2. AUTHORITY
   The Director shall have all rights, powers, and responsibilities as set forth in the Company's
   Articles of Incorporation and Bylaws.

3. COMMITTEE ASSIGNMENTS
   {name} is{committee_text if committee_text else " not assigned to any committees at this time"}.

4. EFFECTIVE DATE
   This resolution shall be effective as of {effective_date}.

5. CERTIFICATION
   The undersigned Secretary certifies that the foregoing resolution was duly adopted by the
   Board of Directors and remains in full force and effect.

Executed this day: {effective_date}

_________________________________
Corporate Secretary

_________________________________
Board Chairperson
"""
        return document.strip()

    @staticmethod
    def generate_nda(data: Dict) -> str:
        """
        Generate a Non-Disclosure Agreement.

        Args:
            data: Dictionary containing NDA information
                - party1_name: First party name
                - party2_name: Second party name
                - effective_date: Effective date
                - term_years: Term in years (optional)

        Returns:
            Formatted NDA document
        """
        party1 = data.get('party1_name', '[PARTY 1 NAME]')
        party2 = data.get('party2_name', '[PARTY 2 NAME]')
        effective_date = data.get('effective_date', '[EFFECTIVE DATE]')
        term_years = data.get('term_years', '2')

        document = f"""
NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement ("Agreement") is entered into as of {effective_date} ("Effective Date")

BETWEEN:

{party1} ("Disclosing Party")

AND:

{party2} ("Receiving Party")

WHEREAS the Disclosing Party possesses certain confidential and proprietary information; and

WHEREAS the Receiving Party desires to receive such confidential information for legitimate business purposes;

NOW THEREFORE, in consideration of the mutual covenants and agreements contained herein, the parties agree as follows:

1. DEFINITION OF CONFIDENTIAL INFORMATION
   "Confidential Information" means any and all technical and non-technical information disclosed by the
   Disclosing Party, including but not limited to: trade secrets, business strategies, customer lists,
   financial information, product designs, software, and any other proprietary information.

2. OBLIGATIONS OF RECEIVING PARTY
   The Receiving Party agrees to:
   a) Hold all Confidential Information in strict confidence
   b) Not disclose Confidential Information to any third party without prior written consent
   c) Use Confidential Information solely for the agreed business purpose
   d) Protect Confidential Information with the same degree of care used for its own confidential information

3. TERM
   This Agreement shall remain in effect for {term_years} years from the Effective Date.
   The obligations regarding Confidential Information shall survive termination for an additional
   {term_years} years.

4. RETURN OF MATERIALS
   Upon termination or upon request, the Receiving Party shall return or destroy all Confidential
   Information and certify such destruction in writing.

5. NO LICENSE
   Nothing in this Agreement grants any license or right to the Receiving Party regarding
   intellectual property of the Disclosing Party.

6. GOVERNING LAW
   This Agreement shall be governed by the laws of the applicable jurisdiction.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.

_________________________________        _________________________________
{party1}                                {party2}
Disclosing Party                        Receiving Party

Date: _______________                   Date: _______________
"""
        return document.strip()

    @staticmethod
    def generate_employment_agreement(data: Dict) -> str:
        """
        Generate an Employment Agreement.

        Args:
            data: Dictionary containing employment information
                - employee_name: Employee name
                - company_name: Company name
                - position: Job position
                - start_date: Start date
                - salary: Annual salary

        Returns:
            Formatted employment agreement document
        """
        employee_name = data.get('employee_name', '[EMPLOYEE NAME]')
        company_name = data.get('company_name', '[COMPANY NAME]')
        position = data.get('position', '[POSITION]')
        start_date = data.get('start_date', '[START DATE]')
        salary = data.get('salary', '[SALARY]')

        document = f"""
EMPLOYMENT AGREEMENT

This Employment Agreement ("Agreement") is entered into as of {start_date}

BETWEEN:

{company_name} ("Company")

AND:

{employee_name} ("Employee")

1. POSITION AND DUTIES
   The Company hereby employs the Employee in the position of {position}. The Employee accepts such
   employment and agrees to perform all duties and responsibilities associated with this position.

2. COMPENSATION
   The Company shall pay the Employee an annual salary of {salary}, payable in accordance with the
   Company's standard payroll practices.

3. START DATE
   Employment shall commence on {start_date}.

4. EMPLOYMENT RELATIONSHIP
   This is an at-will employment relationship. Either party may terminate this agreement at any time,
   with or without cause, with or without notice.

5. DUTIES AND RESPONSIBILITIES
   The Employee shall:
   a) Devote their full business time and attention to the performance of their duties
   b) Comply with all Company policies and procedures
   c) Act in the best interests of the Company at all times
   d) Not engage in any competing business activities

6. CONFIDENTIALITY
   The Employee acknowledges that during employment they will have access to confidential information
   and trade secrets of the Company. The Employee agrees to maintain strict confidentiality of all
   such information during and after employment.

7. BENEFITS
   The Employee shall be eligible for benefits in accordance with Company policies, including but not
   limited to health insurance, paid time off, and retirement plans as applicable.

8. TERMINATION
   Either party may terminate this Agreement with written notice. Upon termination, the Employee shall:
   a) Return all Company property
   b) Continue to maintain confidentiality obligations
   c) Receive final compensation for work performed through the termination date

9. GOVERNING LAW
   This Agreement shall be governed by the laws of the applicable jurisdiction.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

_________________________________        _________________________________
{company_name}                          {employee_name}
Company Representative                   Employee

Date: _______________                   Date: _______________
"""
        return document.strip()

    @staticmethod
    def apply_edit(
        current_document: str,
        edit_type: str,
        field_name: str,
        new_value: str
    ) -> Tuple[str, str]:
        """
        Apply edits to a document.

        Args:
            current_document: The current document text
            edit_type: Type of edit ('update_field', 'replace_section', 'add_clause')
            field_name: Name of field to edit
            new_value: New value to apply

        Returns:
            Tuple of (updated_document, change_description)
        """
        lines = current_document.split('\n')
        updated_lines = []
        changes = []

        for i, line in enumerate(lines):
            if field_name.lower() in line.lower():
                old_line = line

                if edit_type == 'update_field':
                    # Handle different field types
                    if 'effective' in field_name.lower() or 'date' in field_name.lower():
                        # Replace date patterns
                        updated_line = re.sub(
                            r'\[.*?DATE.*?\]|\d{4}-\d{2}-\d{2}|\w+ \d{1,2},? \d{4}',
                            new_value,
                            line
                        )
                    elif 'name' in field_name.lower():
                        # Replace name patterns
                        updated_line = re.sub(
                            r'\[.*?NAME.*?\]|(?<=: ).*$',
                            new_value,
                            line
                        )
                    else:
                        # Generic replacement
                        updated_line = line.replace('[' + field_name.upper() + ']', new_value)

                    if updated_line != old_line:
                        updated_lines.append(updated_line)
                        changes.append(
                            f"Line {i+1}: '{old_line.strip()}' → '{updated_line.strip()}'"
                        )
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        updated_document = '\n'.join(updated_lines)
        change_description = (
            '; '.join(changes) if changes
            else f"Updated {field_name} to {new_value}"
        )

        return updated_document, change_description

    @staticmethod
    def generate(document_type: str, document_data: Dict) -> str:
        """
        Generate a document based on type.

        Args:
            document_type: Type of document to generate
            document_data: Data for document generation

        Returns:
            Generated document text

        Raises:
            ValueError: If document type is not supported
        """
        document_type_lower = document_type.lower()

        if 'director' in document_type_lower or 'appointment' in document_type_lower:
            return DocumentService.generate_director_appointment(document_data)
        elif 'nda' in document_type_lower or 'non-disclosure' in document_type_lower:
            return DocumentService.generate_nda(document_data)
        elif 'employment' in document_type_lower:
            return DocumentService.generate_employment_agreement(document_data)
        else:
            raise ValueError(f"Unsupported document type: {document_type}")

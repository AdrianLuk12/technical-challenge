"""
Function schemas and data models for Gemini function calling.
"""

# Define function declarations for Gemini
FUNCTION_TOOLS = [
    {
        "function_declarations": [
            {
                "name": "extract_information",
                "description": "Extract structured information from the conversation for legal document generation. Use this when you need to gather specific details like names, dates, positions, or other document parameters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_type": {
                            "type": "string",
                            "description": "Type of legal document (e.g., 'director_appointment', 'nda', 'employment_agreement')"
                        },
                        "extracted_data": {
                            "type": "object",
                            "description": "Key-value pairs of extracted information",
                            "properties": {}
                        },
                        "missing_fields": {
                            "type": "array",
                            "description": "List of required fields that are still missing",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["document_type", "extracted_data"]
                }
            },
            {
                "name": "generate_document",
                "description": """Generate a complete legal document based on extracted information. Use this only when you have all required information to create a comprehensive document.

For director appointments, include: director_name, effective_date, committees (optional), resolution_number (optional)
For NDAs, include: party1_name, party2_name, effective_date, term_years (optional)
For employment agreements, include: employee_name, company_name, position, start_date, salary
For custom documents, include: title, sections (array of {heading, content}), date (optional), parties (optional array), and any other relevant fields""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_type": {
                            "type": "string",
                            "description": "Type of legal document to generate (e.g., 'director_appointment', 'nda', 'employment_agreement', or any custom type)"
                        },
                        "document_data": {
                            "type": "object",
                            "description": """All data needed to generate the document. This should be a flat object with key-value pairs.
Examples:
- For director appointment: {"director_name": "John Doe", "effective_date": "2024-03-15", "committees": "Audit Committee", "resolution_number": "RES-2024-001"}
- For NDA: {"party1_name": "Company A", "party2_name": "Company B", "effective_date": "2024-03-15", "term_years": "3"}
- For employment: {"employee_name": "Jane Smith", "company_name": "Acme Corp", "position": "Senior Engineer", "start_date": "2024-04-01", "salary": "$150,000"}""",
                        }
                    },
                    "required": ["document_type", "document_data"]
                }
            },
            {
                "name": "apply_edits",
                "description": "Apply specific edits to an existing document based on user requests. Use this when the user wants to modify, update, or change part of an already generated document.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "edit_type": {
                            "type": "string",
                            "description": "Type of edit (e.g., 'update_field', 'replace_section', 'add_clause')"
                        },
                        "field_name": {
                            "type": "string",
                            "description": "Name of the field or section to edit"
                        },
                        "new_value": {
                            "type": "string",
                            "description": "New value or content to apply"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Brief explanation of the edit"
                        }
                    },
                    "required": ["edit_type", "field_name", "new_value"]
                }
            }
        ]
    }
]

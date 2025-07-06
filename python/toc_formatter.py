#!/usr/bin/env python3
"""
Table of Contents Formatter
Cleans up manually created TOCs by removing messy dots/arrows and applying proper dot leaders.
Also formats abbreviation definitions with professional dot leaders and proper alignment.
"""

import re
import sys
import os
from pathlib import Path
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
import argparse

# Fix Windows encoding issues
if os.name == 'nt':  # Windows
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

class TOCFormatter:
    def __init__(self, input_file, output_file=None):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self.input_file.with_stem(f"{self.input_file.stem}_formatted")
        self.doc = Document(self.input_file)
        
    def is_abbreviation_definition(self, text):
        """
        Check if this line is an abbreviation definition.
        """
        if ':' not in text:
            return False
            
        parts = text.split(':', 1)
        if len(parts) != 2:
            return False
            
        acronym_part = parts[0].strip()
        definition_part = parts[1].strip()
        
        # Pattern to match acronyms (including special characters like β, hyphens, numbers)
        # Using separate character checks to avoid regex syntax issues
        if not (2 <= len(acronym_part) <= 15):
            return False
            
        # Check if acronym starts with letter and contains only valid characters
        if not acronym_part[0].isalpha():
            return False
            
        valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-β')
        if not all(c in valid_chars for c in acronym_part):
            return False
        
        # Check if definition part has dots (indicating it's a messy abbreviation line)
        has_dots = '…' in definition_part or '.' in definition_part
        
        return has_dots
    
    def is_toc_line(self, paragraph):
        """
        Detect if a paragraph is a TOC entry or abbreviation definition.
        """
        text = paragraph.text.strip()
        if not text or len(text) < 5:
            return False
        
        # Check if this is an abbreviation definition
        if self.is_abbreviation_definition(text):
            return True
        
        # Check for regular TOC entries (must end with page number or roman numeral)
        page_pattern = r'([ivxlcdm]+|\d+)\s*$'
        if re.search(page_pattern, text, re.IGNORECASE):
            # Must have reasonable title length
            title_part = re.sub(r'[\.…\s→]+\s*([ivxlcdm]+|\d+)\s*$', '', text, flags=re.IGNORECASE)
            title_part = re.sub(r'^[→\s]+', '', title_part)
            
            if len(title_part.strip()) >= 3:
                return True
        
        return False
    
    def extract_toc_components(self, text):
        """
        Extract title and page number from TOC line, or acronym and definition from abbreviation.
        """
        text = text.strip()
        
        if len(text) < 3:
            return text, "", False
        
        # Check if this is an abbreviation definition first
        if self.is_abbreviation_definition(text):
            parts = text.split(':', 1)
            acronym_part = parts[0].strip()
            definition_part = parts[1].strip()
            
            # Clean up the definition part - remove all dots and extra spaces
            clean_definition = re.sub(r'^[\.…\s]+', '', definition_part)
            clean_definition = re.sub(r'[\.…\s]+$', '', clean_definition)
            
            return acronym_part, clean_definition, True
        
        # Remove leading arrows and dots for regular TOC entries
        text = re.sub(r'^[→\s]+', '', text)
        text = re.sub(r'^[\.…]+\s*', '', text)
        
        # Try different patterns to extract title and page number
        patterns = [
            r'^(.+?)[\.…]{2,}\s*([ivxlcdm]+|\d+)\s*$',
            r'^(.+?)[\.…\s]{3,}([ivxlcdm]+|\d+)\s*$',
            r'^(.+?)\s{2,}([ivxlcdm]+|\d+)\s*$',
            r'^(.+?)\s+([ivxlcdm]+|\d+)\s*$'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                page_num = match.group(2).strip()
                
                # Clean title
                title = re.sub(r'[\.…\s]+$', '', title)
                title = re.sub(r'→+', '', title).strip()
                
                # Validate
                if len(title) >= 2 and len(page_num) <= 6:
                    page_pattern = r'^([ivxlcdm]+|\d+)$'
                    if re.match(page_pattern, page_num, re.IGNORECASE):
                        return title, page_num, False
        
        # Fallback: last word as page number
        words = text.split()
        if words:
            last_word = words[-1].strip()
            page_pattern = r'^([ivxlcdm]+|\d+)$'
            if re.match(page_pattern, last_word, re.IGNORECASE) and len(last_word) <= 6:
                page_num = last_word
                title = ' '.join(words[:-1]).strip()
                
                if len(title) >= 2:
                    title = re.sub(r'[\.…→]+\s*$', '', title).strip()
                    return title, page_num, False
        
        return text, "", False
    
    def get_indentation_level(self, paragraph):
        """
        Determine indentation level.
        """
        text = paragraph.text
        
        # Check Word's paragraph indentation
        paragraph_indent_level = 0
        try:
            if hasattr(paragraph.paragraph_format, 'left_indent') and paragraph.paragraph_format.left_indent:
                indent_inches = paragraph.paragraph_format.left_indent.inches
                if indent_inches >= 1.0:
                    paragraph_indent_level = 2
                elif indent_inches >= 0.3:
                    paragraph_indent_level = 1
        except:
            pass
        
        # Count arrow characters
        leading_arrows = 0
        i = 0
        while i < len(text):
            if text[i] == '→':
                leading_arrows += 1
                i += 1
            elif text[i] in ' \t':
                i += 1
            else:
                break
        
        # Count tabs
        tab_count = 0
        for char in text:
            if char == '\t':
                tab_count += 1
            elif char != ' ':
                break
        
        # Count spaces
        leading_spaces = len(text) - len(text.lstrip(' '))
        
        # Determine final level
        final_level = 0
        
        if paragraph_indent_level > 0:
            final_level = paragraph_indent_level
        elif leading_arrows > 0:
            final_level = min(leading_arrows, 3)
        elif tab_count > 0:
            final_level = min(tab_count, 3)
        elif leading_spaces >= 8:
            final_level = 2
        elif leading_spaces >= 4:
            final_level = 1
        
        # Content-based overrides for main sections
        stripped = text.strip()
        main_keywords = [
            'CHAPTER', 'ABSTRACT', 'INTRODUCTION', 'METHODS', 'RESULTS', 
            'DISCUSSION', 'CONCLUSION', 'REFERENCES', 'ACKNOWLEDGEMENTS', 
            'CITATION', 'DEDICATION', 'LIST OF', 'SUPPORTING MATERIAL', 
            'COMPREHENSIVE', 'MATHEMATICAL'
        ]
        
        for keyword in main_keywords:
            if stripped.upper().startswith(keyword):
                final_level = 0
                break
        
        # Tables and Figures override
        if stripped.startswith(('Table ', 'Figure ')):
            final_level = 0
        
        return final_level
    
    def format_toc_paragraph(self, paragraph, title, page_num_or_definition, indent_level, is_abbreviation=False):
        """
        Apply proper formatting with dot leaders and indentation.
        """
        try:
            if is_abbreviation:
                # Abbreviation: "ACRONYM: \t Definition" with dot leaders aligned to the right
                paragraph.text = f"{title}:\t{page_num_or_definition}"
                tab_position = 6.5  # Same position as TOC entries for consistent alignment
                alignment = WD_TAB_ALIGNMENT.RIGHT
            else:
                # Regular TOC entry: "Title \t PageNum"
                paragraph.text = f"{title}\t{page_num_or_definition}"
                tab_position = 6.5  # Position for page numbers
                alignment = WD_TAB_ALIGNMENT.RIGHT
            
            # Set indentation (abbreviations get no indentation)
            if is_abbreviation:
                base_indent = 0
            else:
                base_indent = indent_level * 0.25
            
            paragraph.paragraph_format.left_indent = Inches(base_indent)
            paragraph.paragraph_format.first_line_indent = Inches(0)
            
            # Clear and set tab stops with dot leaders
            paragraph.paragraph_format.tab_stops.clear_all()
            paragraph.paragraph_format.tab_stops.add_tab_stop(
                Inches(tab_position),
                alignment,
                WD_TAB_LEADER.DOTS
            )
            
            # Set line spacing
            paragraph.paragraph_format.line_spacing = 1.0
            paragraph.paragraph_format.space_after = Inches(0)
            paragraph.paragraph_format.space_before = Inches(0)
                
        except Exception as e:
            print(f"    Warning: Could not format paragraph: {e}")
            if is_abbreviation:
                paragraph.text = f"{title}: {page_num_or_definition}"
            else:
                paragraph.text = f"{title}\t{page_num_or_definition}"
    
    def process_document(self):
        """
        Process the entire document.
        """
        toc_count = 0
        
        print(f"Processing: {self.input_file.name}")
        
        for paragraph in self.doc.paragraphs:
            if self.is_toc_line(paragraph):
                original_text = paragraph.text
                title, page_num_or_definition, is_abbrev = self.extract_toc_components(original_text)
                
                if title and page_num_or_definition:
                    if is_abbrev:
                        # Abbreviation definition
                        self.format_toc_paragraph(paragraph, title, page_num_or_definition, 0, is_abbreviation=True)
                        toc_count += 1
                        print(f"  Formatted: {title}: {page_num_or_definition[:40]} (abbreviation)")
                    else:
                        # Regular TOC entry with page number
                        indent_level = self.get_indentation_level(paragraph)
                        self.format_toc_paragraph(paragraph, title, page_num_or_definition, indent_level, is_abbreviation=False)
                        toc_count += 1
                        
                        indent_indicator = "  " * indent_level
                        print(f"  Formatted: {indent_indicator}{title[:40]} -> {page_num_or_definition} (level {indent_level})")
                elif title:
                    print(f"  Formatted: {title[:60]} (header)")
                    toc_count += 1
                else:
                    print(f"  Skipped: {original_text[:60]}")
        
        print(f"\nFormatted {toc_count} entries")
        return toc_count
    
    def save(self):
        """
        Save the document.
        """
        try:
            self.doc.save(self.output_file)
            print(f"Saved: {self.output_file}")
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Format table of contents and abbreviations in Word documents")
    parser.add_argument('input_file', help='Input Word document (.docx)')
    parser.add_argument('-o', '--output', help='Output file (default: input_formatted.docx)')
    parser.add_argument('--backup', action='store_true', help='Create backup of original file')
    
    args = parser.parse_args()
    
    # Validate input
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File '{input_path}' not found")
        sys.exit(1)
    
    if input_path.suffix.lower() != '.docx':
        print("Error: Input file must be a .docx document")
        sys.exit(1)
    
    # Create backup if requested
    if args.backup:
        backup_path = input_path.with_stem(f"{input_path.stem}_backup")
        try:
            import shutil
            shutil.copy2(input_path, backup_path)
            print(f"Backup created: {backup_path}")
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
    
    # Process document
    try:
        formatter = TOCFormatter(args.input_file, args.output)
        count = formatter.process_document()
        
        if count > 0:
            if formatter.save():
                print(f"\nSUCCESS: Successfully formatted {count} entries")
                print(f"Output: {formatter.output_file}")
                print("\nFeatures applied:")
                print("• Removed arrows and messy dots")
                print("• Added professional dot leaders")
                print("• Detected hierarchy from Word's paragraph formatting")
                print("• Right-aligned page numbers for TOC entries")
                print("• Right-aligned definitions for abbreviations")
                print("• Support for Roman numerals")
                print("• Support for special characters")
            else:
                print("\nERROR: Failed to save document")
                sys.exit(1)
        else:
            print("\nWARNING: No entries detected")
    
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
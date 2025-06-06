import logging
import os
import io
import re
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Tuple, Optional
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)

# Set style for matplotlib
plt.style.use('dark_background')
sns.set_style("darkgrid")
sns.set_context("notebook", font_scale=1.2)

# Custom color palettes for medical infographics
MEDICAL_COLORS = {
    'primary': ['#0077CC', '#3399FF', '#66B2FF', '#99CCFF', '#CCE5FF'],
    'alert': ['#FF3333', '#FF6666', '#FF9999', '#FFCCCC', '#FFE5E5'],
    'neutral': ['#5C5C5C', '#7A7A7A', '#999999', '#B8B8B8', '#D6D6D6'],
    'positive': ['#00CC66', '#33FF99', '#66FFCC', '#99FFDD', '#CCFFEE'],
    'highlight': ['#FF6600', '#FF9933', '#FFCC66', '#FFE599', '#FFF2CC']
}

def generate_medical_terms_chart(medical_terms: List[str], sections: Dict[str, str]) -> Tuple[Optional[str], str]:
    """
    Generate a chart visualizing the medical terms and their frequencies in different sections.
    
    Args:
        medical_terms: List of identified medical terms
        sections: Dictionary of report sections
        
    Returns:
        Tuple containing the base64 encoded image (or None) and HTML for the chart
    """
    try:
        if not medical_terms:
            return None, "<div class='alert alert-info'>No medical terms identified for visualization.</div>"
        
        # Count term occurrences
        term_counts = {}
        for term in medical_terms:
            term_counts[term] = 0
            for section_text in sections.values():
                # Case-insensitive count
                term_counts[term] += len([m.start() for m in re.finditer(re.escape(term), section_text, re.IGNORECASE)])
        
        # Sort by frequency and take top 10 for better visualization
        term_counts = dict(sorted(term_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Generate bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(list(term_counts.keys()), list(term_counts.values()), 
                        color=MEDICAL_COLORS['primary'][0], alpha=0.8)
        
        # Add count labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.2, bar.get_y() + bar.get_height()/2, 
                    f"{width}", ha='left', va='center', fontweight='bold')
        
        ax.set_title('Frequency of Medical Terms in Report', fontsize=16, pad=20)
        ax.set_xlabel('Number of Occurrences', fontsize=12)
        ax.set_ylabel('Medical Terms', fontsize=12)
        sns.despine(left=True, bottom=True)
        plt.tight_layout()
        
        # Save figure to a base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        # Create interactive version with Plotly
        fig = go.Figure(go.Bar(
            x=list(term_counts.values()),
            y=list(term_counts.keys()),
            orientation='h',
            marker=dict(color=MEDICAL_COLORS['primary'][0]),
            text=list(term_counts.values()),
            textposition='outside'
        ))
        
        fig.update_layout(
            title='Frequency of Medical Terms in Report',
            xaxis_title='Number of Occurrences',
            yaxis_title='Medical Terms',
            template='plotly_dark',
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        plotly_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        return img_str, plotly_html
        
    except Exception as e:
        logger.error(f"Error generating medical terms chart: {str(e)}")
        return None, f"<div class='alert alert-danger'>Failed to generate visualization: {str(e)}</div>"

def generate_section_breakdown_chart(sections: Dict[str, str]) -> Tuple[Optional[str], str]:
    """
    Generate a chart visualizing the relative sizes of each report section.
    
    Args:
        sections: Dictionary of report sections
        
    Returns:
        Tuple containing the base64 encoded image (or None) and HTML for the chart
    """
    try:
        if not sections:
            return None, "<div class='alert alert-info'>No report sections available for visualization.</div>"
        
        # Calculate section lengths
        section_lengths = {name: len(text) for name, text in sections.items()}
        
        # Generate pie chart
        fig, ax = plt.subplots(figsize=(8, 8))
        wedges, texts, autotexts = ax.pie(
            section_lengths.values(), 
            labels=section_lengths.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=MEDICAL_COLORS['primary'],
            wedgeprops=dict(width=0.5, edgecolor='w')
        )
        
        # Style the text elements
        for text in texts:
            text.set_fontsize(11)
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
            
        ax.set_title('Report Section Distribution', fontsize=16, pad=20)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.tight_layout()
        
        # Save figure to a base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        # Create interactive version with Plotly
        fig = px.pie(
            values=list(section_lengths.values()),
            names=list(section_lengths.keys()),
            hole=0.4,
            title='Report Section Distribution'
        )
        
        fig.update_layout(
            template='plotly_dark',
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            marker=dict(line=dict(color='#FFFFFF', width=1))
        )
        
        plotly_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        return img_str, plotly_html
        
    except Exception as e:
        logger.error(f"Error generating section breakdown chart: {str(e)}")
        return None, f"<div class='alert alert-danger'>Failed to generate visualization: {str(e)}</div>"

def generate_conditions_chart(conditions: List[str]) -> Tuple[Optional[str], str]:
    """
    Generate a visualization of predicted conditions.
    
    Args:
        conditions: List of predicted conditions
        
    Returns:
        Tuple containing the base64 encoded image (or None) and HTML for the chart
    """
    try:
        if not conditions or conditions[0] == "No specific conditions identified":
            return None, "<div class='alert alert-info'>No conditions identified for visualization.</div>"
        
        # Limit to top 8 conditions for clarity
        if len(conditions) > 8:
            display_conditions = conditions[:8]
        else:
            display_conditions = conditions
            
        # Generate confidence scores (for demonstration - in a real app these would come from analysis)
        confidence_scores = np.linspace(0.9, 0.4, len(display_conditions))
        
        # Generate horizontal bar chart with fake confidence scores
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create color gradient
        colors = []
        for score in confidence_scores:
            if score >= 0.7:
                colors.append(MEDICAL_COLORS['alert'][0])  # High confidence - red
            elif score >= 0.5:
                colors.append(MEDICAL_COLORS['highlight'][0])  # Medium confidence - orange
            else:
                colors.append(MEDICAL_COLORS['neutral'][0])  # Low confidence - gray
        
        bars = ax.barh(display_conditions, confidence_scores * 100, color=colors, alpha=0.8)
        
        # Add percentage labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                    f"{width:.1f}%", ha='left', va='center', fontweight='bold')
        
        ax.set_title('Predicted Conditions with Confidence Levels', fontsize=16, pad=20)
        ax.set_xlabel('Confidence Level (%)', fontsize=12)
        ax.set_xlim(0, 100)
        ax.set_ylabel('Potential Conditions', fontsize=12)
        
        # Add a note about the artificial confidence scores
        ax.text(0, -1.5, '* Confidence scores are estimated for visualization purposes', 
                fontsize=8, style='italic', color='gray')
        
        sns.despine(left=True, bottom=True)
        plt.tight_layout()
        
        # Save figure to a base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        # Create interactive version with Plotly
        fig = go.Figure()
        
        for i, condition in enumerate(display_conditions):
            fig.add_trace(go.Bar(
                x=[confidence_scores[i] * 100],
                y=[condition],
                orientation='h',
                marker=dict(color=colors[i]),
                text=[f"{confidence_scores[i] * 100:.1f}%"],
                textposition='outside',
                name=condition
            ))
        
        fig.update_layout(
            title='Predicted Conditions with Confidence Levels',
            xaxis_title='Confidence Level (%)',
            yaxis_title='Potential Conditions',
            xaxis=dict(range=[0, 100]),
            template='plotly_dark',
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False,
            annotations=[
                dict(
                    text="* Confidence scores are estimated for visualization purposes",
                    xref="paper", yref="paper",
                    x=0, y=-0.1,
                    showarrow=False,
                    font=dict(size=10, color="gray"),
                    align="left"
                )
            ]
        )
        
        plotly_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        return img_str, plotly_html
        
    except Exception as e:
        logger.error(f"Error generating conditions chart: {str(e)}")
        return None, f"<div class='alert alert-danger'>Failed to generate visualization: {str(e)}</div>"

def extract_clinical_history(text: str) -> str:
    """
    Extract clinical history from report text.
    
    Args:
        text: Full report text
        
    Returns:
        Extracted clinical history or a default message
    """
    try:
        # Look for common clinical history patterns
        history_patterns = [
            r"(?i)clinical (?:history|info|information):?\s*([^\n.]+(?:\n|\.)?)",
            r"(?i)history:?\s*([^\n.]+(?:\n|\.)?)",
            r"(?i)indication:?\s*([^\n.]+(?:\n|\.)?)",
            r"(?i)reason for (?:exam|examination|study|imaging|scan):?\s*([^\n.]+(?:\n|\.)?)"
        ]
        
        for pattern in history_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        # Default if no history found
        return "No clinical history provided"
    except Exception as e:
        logger.error(f"Error extracting clinical history: {str(e)}")
        return "Unable to extract clinical history"

def extract_imaging_techniques(text: str, sections: Dict[str, str]) -> List[str]:
    """
    Extract imaging techniques from the report.
    
    Args:
        text: Full report text
        sections: Report sections
        
    Returns:
        List of identified imaging techniques
    """
    try:
        # Common imaging techniques and their variations
        technique_patterns = [
            r"(?i)(?:performed|obtained|acquired) (?:with|using) ([^.]+)",
            r"(?i)(?:technique|protocol):?\s*([^\n.]+(?:\n|\.)?)",
            r"(?i)(t1(?:-weighted)?(?:\s+\w+)?)",
            r"(?i)(t2(?:-weighted)?(?:\s+\w+)?)",
            r"(?i)(flair)",
            r"(?i)(dwi|diffusion weighted)",
            r"(?i)(swi|susceptibility weighted)",
            r"(?i)(adc|apparent diffusion coefficient)",
            r"(?i)(stir)",
            r"(?i)(contrast(?:-enhanced)?)",
            r"(?i)(non-contrast)",
            r"(?i)(pre(?:\s+and\s+|\s+)?post(?:\s+)?contrast)",
            r"(?i)(with(?:\s+and\s+without|\s+)?gadolinium)",
            r"(?i)(sagittal|axial|coronal)(?:\s+\w+)?"
        ]
        
        techniques = set()
        
        # Look in technique section first if it exists
        for section_name, section_text in sections.items():
            if "technique" in section_name.lower():
                for pattern in technique_patterns:
                    matches = re.finditer(pattern, section_text)
                    for match in matches:
                        technique = match.group(1).strip()
                        techniques.add(technique)
        
        # Look in the full text
        if not techniques:
            for pattern in technique_patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    technique = match.group(1).strip()
                    techniques.add(technique)
        
        # Return a list of identified techniques, or default list if none found
        if techniques:
            return sorted(list(techniques))
        else:
            return ["Standard protocol images", "T1-weighted sequence", "T2-weighted sequence"]
    except Exception as e:
        logger.error(f"Error extracting imaging techniques: {str(e)}")
        return ["Imaging technique information not available"]

def extract_measurements(text: str) -> List[Dict[str, str]]:
    """
    Extract measurements from the report.
    
    Args:
        text: Full report text
        
    Returns:
        List of dictionaries containing measurement details
    """
    try:
        # Patterns to match measurements (size descriptions)
        measurement_patterns = [
            # Common patterns for measurements in medical reports
            r"(?i)(?:measures|measuring|sized?|approximately)(?:\s+about)?\s+(\d+(?:\.\d+)?(?:\s*x\s*\d+(?:\.\d+)?(?:\s*x\s*\d+(?:\.\d+)?)?)?)\s*(?:cm|mm)",
            r"(?i)(\d+(?:\.\d+)?(?:\s*[×x]\s*\d+(?:\.\d+)?(?:\s*[×x]\s*\d+(?:\.\d+)?)?)?)\s*(?:cm|mm)(?:\s+(?:lesion|mass|nodule|tumor|cyst|area|region))?",
            r"(?i)(?:lesion|mass|nodule|tumor|cyst|area|region)(?:\s+(?:of|with|measuring))?\s+(?:approximately|about|nearly)?\s*(\d+(?:\.\d+)?(?:\s*[×x]\s*\d+(?:\.\d+)?(?:\s*[×x]\s*\d+(?:\.\d+)?)?)?)\s*(?:cm|mm)"
        ]
        
        # Look for descriptions of location with measurements
        location_patterns = [
            r"(?i)(?:in|at|on|within|involving)\s+the\s+([a-z]+(?:\s+[a-z]+)?(?:\s+[a-z]+)?)",
            r"(?i)(?:located|situated|found|seen|visualized|noted)\s+(?:in|at|on)?\s+(?:the)?\s+([a-z]+(?:\s+[a-z]+)?(?:\s+[a-z]+)?)"
        ]
        
        measurements = []
        
        # Find all measurements in the text
        for pattern in measurement_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                # Get the measurement
                measurement = match.group(1).strip()
                
                # Get the surrounding text (30 characters before and after) to find location
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end]
                
                # Look for location in the context
                location = "unspecified location"
                for loc_pattern in location_patterns:
                    loc_match = re.search(loc_pattern, context)
                    if loc_match:
                        location = loc_match.group(1).strip()
                        break
                
                measurements.append({
                    "size": measurement,
                    "location": location
                })
        
        return measurements if measurements else [{"size": "measurements not provided", "location": "not specified"}]
    except Exception as e:
        logger.error(f"Error extracting measurements: {str(e)}")
        return [{"size": "error extracting measurements", "location": "error"}]

def extract_contrast_info(text: str) -> str:
    """
    Extract contrast agent information from the report.
    
    Args:
        text: Full report text
        
    Returns:
        String describing contrast usage
    """
    try:
        # Patterns to match contrast agent information
        contrast_patterns = [
            r"(?i)(\d+(?:\.\d+)?)\s*(?:cc|ml)\s+(?:of\s+)?([a-zA-Z]+)(?:\s+contrast)?",
            r"(?i)([a-zA-Z]+)\s+contrast,?\s+(\d+(?:\.\d+)?)\s*(?:cc|ml)",
            r"(?i)(?:with|using)\s+(?:intravenous|IV)?\s+(?:contrast|([a-zA-Z]+))"
        ]
        
        for pattern in contrast_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) > 1 and match.group(1) and match.group(2):
                    return f"{match.group(1)} cc {match.group(2)} contrast administered"
                elif match.group(1):
                    return f"{match.group(1)} contrast administered"
        
        # Check if explicitly no contrast
        no_contrast_pattern = r"(?i)(?:without|no|non[- ]?contrast)"
        if re.search(no_contrast_pattern, text):
            return "No contrast administered"
        
        return "Contrast information not specified"
    except Exception as e:
        logger.error(f"Error extracting contrast information: {str(e)}")
        return "Unable to determine contrast usage"

def extract_key_findings(text: str, sections: Dict[str, str]) -> List[str]:
    """
    Extract key findings from the report.
    
    Args:
        text: Full report text
        sections: Report sections
        
    Returns:
        List of key findings
    """
    try:
        findings = []
        
        # Common negative findings to look for
        negative_patterns = [
            r"(?i)no (?:evidence of|signs of|acute|findings of)?\s+([a-z]+(?:\s+[a-z]+)?(?:\s+[a-z]+)?)",
            r"(?i)(?:absence|lack) of\s+([a-z]+(?:\s+[a-z]+)?(?:\s+[a-z]+)?)",
            r"(?i)(?:normal|unremarkable)\s+([a-z]+(?:\s+[a-z]+)?)"
        ]
        
        # Common positive findings to look for
        positive_patterns = [
            r"(?i)(?:evidence of|presence of|shows|demonstrates|reveals)\s+([a-z]+(?:\s+[a-z]+)?(?:\s+[a-z]+)?)",
            r"(?i)([a-z]+(?:\s+[a-z]+)?)\s+(?:is|are)\s+(?:seen|noted|visualized|identified|present)"
        ]
        
        # Check findings and impression sections first
        for section_name, section_text in sections.items():
            if section_name.lower() in ['findings', 'impression', 'conclusion']:
                # Split by sentences or bullet points
                sentences = re.split(r'(?<=[.!?])\s+|\n+', section_text)
                for sentence in sentences:
                    if sentence.strip():
                        # Only add sentences that aren't too long
                        if len(sentence.strip()) < 100:
                            findings.append(sentence.strip())
                
                # If we have 3 or more findings, return them
                if len(findings) >= 3:
                    return findings[:5]  # Limit to 5 findings
        
        # If we don't have enough findings from sections, look for patterns
        if len(findings) < 3:
            # Look for negative findings
            for pattern in negative_patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    finding = f"No {match.group(1).strip()}"
                    if finding not in findings:
                        findings.append(finding)
            
            # Look for positive findings
            for pattern in positive_patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    finding = match.group(1).strip()
                    if finding and finding not in findings:
                        findings.append(finding)
        
        return findings[:5] if findings else ["No specific findings extracted"]
    except Exception as e:
        logger.error(f"Error extracting key findings: {str(e)}")
        return ["Unable to extract key findings"]

def generate_full_infographic(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a complete infographic for the medical report.
    
    Args:
        report_data: The processed report data
        
    Returns:
        Dictionary containing base64 encoded images and HTML for the infographic
    """
    try:
        logger.info("Generating infographic for medical report")
        
        processed_data = report_data.get('processed_data', {})
        sections = processed_data.get('sections', {})
        medical_terms = processed_data.get('medical_terms', [])
        conditions = report_data.get('conditions', [])
        original_text = report_data.get('original_text', '')
        
        # Generate individual charts
        terms_img, terms_html = generate_medical_terms_chart(medical_terms, sections)
        sections_img, sections_html = generate_section_breakdown_chart(sections)
        conditions_img, conditions_html = generate_conditions_chart(conditions)
        
        # Extract additional clinical context
        clinical_history = extract_clinical_history(original_text)
        imaging_techniques = extract_imaging_techniques(original_text, sections)
        measurements = extract_measurements(original_text)
        contrast_info = extract_contrast_info(original_text)
        key_findings = extract_key_findings(original_text, sections)
        
        # Organize differential diagnoses into primary and secondary
        if conditions and conditions[0] != "No specific conditions identified":
            primary_condition = conditions[0] if len(conditions) > 0 else None
            secondary_conditions = conditions[1:] if len(conditions) > 1 else []
        else:
            primary_condition = None
            secondary_conditions = []
        
        # Combine charts and extracted information into full infographic
        infographic = {
            'terms_chart': {
                'image': terms_img,
                'html': terms_html
            },
            'sections_chart': {
                'image': sections_img,
                'html': sections_html
            },
            'conditions_chart': {
                'image': conditions_img,
                'html': conditions_html
            },
            'clinical_context': {
                'history': clinical_history,
                'techniques': imaging_techniques,
                'measurements': measurements,
                'contrast': contrast_info,
                'key_findings': key_findings,
                'primary_condition': primary_condition,
                'secondary_conditions': secondary_conditions
            }
        }
        
        logger.debug("Successfully generated infographic")
        return infographic
        
    except Exception as e:
        logger.error(f"Error generating infographic: {str(e)}")
        return {
            'error': str(e),
            'terms_chart': {'image': None, 'html': f"<div class='alert alert-danger'>Error generating chart: {str(e)}</div>"},
            'sections_chart': {'image': None, 'html': ""},
            'conditions_chart': {'image': None, 'html': ""},
            'clinical_context': {
                'history': "Error generating clinical context",
                'techniques': [],
                'measurements': [],
                'contrast': "Error",
                'key_findings': [],
                'primary_condition': None,
                'secondary_conditions': []
            }
        }
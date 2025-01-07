from typing import List
from pydantic import BaseModel, Field
from ..base import STIPPrompt


class ThemeInfo(BaseModel):
    """Single theme with code, label and reasoning"""
    theme_code: str = Field(description="Code of the theme")
    label: str = Field(
        description="Label of the theme as provided in the reference data")
    reason: str = Field(
        description="Reasoning for why this theme applies", max_length=200)


REFERENCE_DATA = {
    "themes": [
        {
            "code": "TH20",
            "label": "Public research|Public research strategy",
            "question": "What strategies or plans exist, if any, to strategically direct government support to public research?"
        },
        {
            "code": "TH21",
            "label": "Public research|Institutional funding of public research",
            "question": "What are the main policy initiatives for providing institutional funding to public research?"
        },
        {
            "code": "TH22",
            "label": "Public research|Project-based funding of public research",
            "question": "What are the main policy initiatives for providing project-based funding to public research?"
        },
        {
            "code": "TH23",
            "label": "Public research|Research infrastructures",
            "question": "What policy initiatives exist to support research infrastructures?"
        },
        {
            "code": "TH24",
            "label": "Public research|Open science",
            "question": "What policy initiatives exist to promote open science?"
        },
        {
            "code": "TH30",
            "label": "Innovation in firms and innovative entrepreneurship|Innovation in firms strategy",
            "question": "What strategies or plans exist, if any, to strategically direct government support to innovation in firms?"
        },
        {
            "code": "TH31",
            "label": "Innovation in firms and innovative entrepreneurship|Financial support to business R&D and innovation",
            "question": "What are the main policy initiatives for providing financial support to business R&D and innovation?"
        },
        {
            "code": "TH32",
            "label": "Innovation in firms and innovative entrepreneurship|Non-financial support to business R&D and innovation",
            "question": "What are the main policy initiatives for providing non-financial support to business R&D and innovation?"
        },
        {
            "code": "TH33",
            "label": "Innovation in firms and innovative entrepreneurship|Innovation in services",
            "question": "What policy initiatives exist to promote innovation in services?"
        },
        {
            "code": "TH34",
            "label": "Innovation in firms and innovative entrepreneurship|Foreign direct investment and technology transfer",
            "question": "What policy initiatives exist to attract knowledge-intensive foreign direct investment and promote transfers to domestic firms?"
        },
        {
            "code": "TH35",
            "label": "Innovation in firms and innovative entrepreneurship|Targeted support to SMEs and young innovative enterprises",
            "question": "What are the main policy initiatives specifically targeting research and innovation activities in SMEs, start-ups and young innovative enterprises?"
        },
        {
            "code": "TH41",
            "label": "Knowledge exchange and co-creation|Knowledge exchange and co-creation strategies",
            "question": "What strategies or plans exist, if any, to strategically direct government support for knowledge exchange and co-creation?"
        },
        {
            "code": "TH42",
            "label": "Knowledge exchange and co-creation|Collaborative research and innovation",
            "question": "What are the main policy initiatives to promote collaboration between public researchers and other stakeholders, including business and citizens?"
        },
        {
            "code": "TH47",
            "label": "Knowledge exchange and co-creation|Cluster policies",
            "question": "What policy initiatives exist to promote geographical and/or thematic innovative clusters?"
        },
        {
            "code": "TH43",
            "label": "Knowledge exchange and co-creation|Commercialisation of public research results",
            "question": "What policy initiatives exist to encourage commercialisation of public research results?"
        },
        {
            "code": "TH44",
            "label": "Knowledge exchange and co-creation|Inter-sectoral mobility",
            "question": "What policy initiatives exist to encourage mobility of human resources between the public and private sectors?"
        },
        {
            "code": "TH46",
            "label": "Knowledge exchange and co-creation|Intellectual property rights in public research",
            "question": "What policy initiatives exist to ensure intellectual property rights in public research are conducive to promoting innovation?"
        },
        {
            "code": "TH50",
            "label": "Human resources for research and innovation|STI human resources strategies",
            "question": "What strategies or plans exist, if any, to strategically direct government support to human resources for research and innovation?"
        },
        {
            "code": "TH51",
            "label": "Human resources for research and innovation|STEM skills",
            "question": "What are the main policy initiatives for nurturing general STEM skills?"
        },
        {
            "code": "TH52",
            "label": "Human resources for research and innovation|Doctoral and postdoctoral researchers",
            "question": "What policy initiatives exist to specifically support doctoral and postdoctoral research and education?"
        },
        {
            "code": "TH53",
            "label": "Human resources for research and innovation|Research careers",
            "question": "What policy initiatives exist to make research careers more attractive?"
        },
        {
            "code": "TH55",
            "label": "Human resources for research and innovation|International mobility of human resources",
            "question": "What policy initiatives exist to encourage international mobility of researchers?"
        },
        {
            "code": "TH54",
            "label": "Human resources for research and innovation|Equity, diversity and inclusion (EDI)",
            "question": "What policy initiatives exist to promote the participation of women and other under-represented groups in research and innovation activities?"
        },
        {
            "code": "TH58",
            "label": "Research and innovation for society|Research and innovation for society strategy",
            "question": "What strategies or plans exist, if any, to strategically direct government support for research and innovation specifically targeted at societal well-being and cohesion?"
        },
        {
            "code": "TH91",
            "label": "Research and innovation for society|Mission-oriented innovation policies",
            "question": "What cross-government initiatives exist, if any, to coordinate and jointly operate different policy initiatives to achieve ambitious goals within a defined timeframe and to address a societal challenge?"
        },
        {
            "code": "TH89",
            "label": "Research and innovation for society|Ethics of emerging technologies",
            "question": "What policy initiatives exist, if any, to address ethical challenges raised by emerging technologies?"
        },
        {
            "code": "TH61",
            "label": "Research and innovation for society|Research and innovation for developing countries",
            "question": "What policy initiatives exist, if any, specifically dedicated to supporting research and innovation in developing and less technologically advanced countries?"
        },
        {
            "code": "TH65",
            "label": "Research and innovation for society|Multi-stakeholder engagement",
            "question": "What policy initiatives exist to promote a broad and diversified public engagement in research and innovation activities and policy making?"
        },
        {
            "code": "TH66",
            "label": "Research and innovation for society|Science, technology and innovation culture",
            "question": "What are the main policy initiatives for building understandings and common STI culture across technical communities and citizens?"
        },
        {
            "code": "TH102",
            "label": "Net zero transitions|Government capabilities for net zero transitions",
            "question": "What reforms, if any, have been implemented to improve the operation and capabilities of STI ministries and agencies to better address net zero transitions?"
        },
        {
            "code": "TH92",
            "label": "Net zero transitions|Net zero transitions in energy",
            "question": "What policy initiatives, if any, aim specifically to support research and innovation for net-zero carbon ambitions in the energy sector?"
        },
        {
            "code": "TH103",
            "label": "Net zero transitions|Net zero transitions in transport and mobility",
            "question": "What policy initiatives, if any, aim specifically to support research and innovation for net-zero carbon ambitions in the transport and mobility sectors?"
        },
        {
            "code": "TH104",
            "label": "Net zero transitions|Net zero transitions in food and agriculture",
            "question": "What policy initiatives, if any, aim specifically to support research and innovation for net-zero carbon ambitions in the food and agriculture sectors?"
        },
        {
            "code": "TH105",
            "label": "Net zero transitions|STI policies for net zero",
            "question": "Please link to this question policies in other sections of the questionnaire that prominently aim to achieve net zero carbon ambitions."
        }
    ]
}


themes_prompt = STIPPrompt(
    name="themes",
    description="Identify main and secondary themes of the initiative",
    system_message="""You are a policy analyst specializing in thematic classification of STI initiatives.
    Your task is to identify the main themes that best describe the initiative's focus.
    Only select themes that are explicitly mentioned or clearly implied in the text.
    Provide clear reasoning for each match.""",
    template="""Consider yourself an expert policy analyst. Identify which theme(s) 
    best describe the {initiative_name} initiative. Match them to the provided theme definitions 
    and provide reasoning for each match. Select one main theme and up to two secondary themes.
    
    If no relevant themes are found, return an empty list.""",
    response_fields={
        "themes": (List[ThemeInfo], Field(
            description="List of themes, ordered by relevance (main theme first)",
            default_factory=list
        ))
    },
    reference_data=REFERENCE_DATA
)

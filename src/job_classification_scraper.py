"""
Job Classification Web Scraper
Automated scraper for extracting job titles and SOC codes from government job portals
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import re
import csv
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse, parse_qs
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class JobClassification:
    """Data class for job classification information - matches standardized intake format"""
    JobCode: str
    JobTitleAbbreviation: str
    JobTitleFull: str
    OccupationalGroupText: str
    EEOText: str
    WorkFunction: str
    WorkLevel: str
    SupervisionReceived: str


# EEO (Equal Employment Opportunity) Category Mappings based on SOC codes
EEO_CATEGORIES = {
    "11": "Officials and Administrators",
    "13": "Professionals",
    "15": "Technicians",
    "17": "Professionals",
    "19": "Professionals",
    "21": "Professionals",
    "23": "Professionals",
    "25": "Professionals",
    "27": "Professionals",
    "29": "Professionals",
    "31": "Paraprofessionals",
    "33": "Protective Service Workers",
    "35": "Service-Maintenance",
    "37": "Service-Maintenance",
    "39": "Service-Maintenance",
    "41": "Administrative Support",
    "43": "Administrative Support",
    "45": "Skilled Craft Workers",
    "47": "Skilled Craft Workers",
    "49": "Skilled Craft Workers",
    "51": "Skilled Craft Workers",
    "53": "Service-Maintenance",
}

# Work Level Mappings
WORK_LEVELS = {
    "I": "Entry Level",
    "II": "Journey Level",
    "III": "Senior Level",
    "IV": "Advanced Level",
    "Director": "Executive",
    "Manager": "Management",
    "Supervisor": "Supervisory",
    "Chief": "Executive",
    "Administrator": "Management",
    "Coordinator": "Professional",
    "Specialist": "Professional",
    "Analyst": "Professional",
    "Technician": "Technical",
    "Assistant": "Support",
    "Aide": "Entry Level",
    "Clerk": "Support",
}

# Supervision Received Mappings
SUPERVISION_LEVELS = {
    "Director": "Minimal - Reports to Executive Leadership",
    "Manager": "General - Reports to Director/Executive",
    "Supervisor": "General - Reports to Manager",
    "Chief": "Minimal - Reports to Executive Leadership",
    "III": "Limited - Works independently with periodic review",
    "II": "Moderate - Regular supervision with some independence",
    "I": "Close - Direct supervision, work reviewed frequently",
    "Specialist": "Limited - Works independently with periodic review",
    "Analyst": "Limited - Works independently with periodic review",
    "Technician": "Moderate - Regular supervision with some independence",
    "Assistant": "Close - Direct supervision, work reviewed frequently",
    "Aide": "Close - Direct supervision, work reviewed frequently",
    "Clerk": "Close - Direct supervision, work reviewed frequently",
}


class SOCCodeMapper:
    """
    Maps job titles to Standard Occupational Classification (SOC) codes
    Uses BLS SOC code database for standardized mapping
    """

    def __init__(self):
        self.soc_database = self._build_soc_database()

    def _build_soc_database(self) -> Dict[str, Tuple[str, str]]:
        """
        Build SOC code database with common government job mappings
        Format: keyword -> (SOC code, SOC title)
        """
        return {
            # Management Occupations (11-0000)
            "chief executive": ("11-1011", "Chief Executives"),
            "executive director": ("11-1011", "Chief Executives"),
            "general manager": ("11-1021", "General and Operations Managers"),
            "operations manager": ("11-1021", "General and Operations Managers"),
            "administrator": ("11-1021", "General and Operations Managers"),
            "advertising manager": ("11-2011", "Advertising and Promotions Managers"),
            "marketing manager": ("11-2021", "Marketing Managers"),
            "sales manager": ("11-2022", "Sales Managers"),
            "public relations manager": ("11-2031", "Public Relations Managers"),
            "administrative services manager": ("11-3012", "Administrative Services Managers"),
            "facilities manager": ("11-3013", "Facilities Managers"),
            "computer information systems manager": ("11-3021", "Computer and Information Systems Managers"),
            "it manager": ("11-3021", "Computer and Information Systems Managers"),
            "information technology manager": ("11-3021", "Computer and Information Systems Managers"),
            "financial manager": ("11-3031", "Financial Managers"),
            "comptroller": ("11-3031", "Financial Managers"),
            "treasurer": ("11-3031", "Financial Managers"),
            "human resources manager": ("11-3121", "Human Resources Managers"),
            "hr manager": ("11-3121", "Human Resources Managers"),
            "personnel manager": ("11-3121", "Human Resources Managers"),
            "training manager": ("11-3131", "Training and Development Managers"),
            "purchasing manager": ("11-3061", "Purchasing Managers"),
            "procurement manager": ("11-3061", "Purchasing Managers"),
            "transportation manager": ("11-3071", "Transportation, Storage, and Distribution Managers"),
            "construction manager": ("11-9021", "Construction Managers"),
            "education administrator": ("11-9032", "Education Administrators, Kindergarten through Secondary"),
            "principal": ("11-9032", "Education Administrators, Kindergarten through Secondary"),
            "superintendent": ("11-9033", "Education Administrators, Postsecondary"),
            "engineering manager": ("11-9041", "Architectural and Engineering Managers"),
            "food service manager": ("11-9051", "Food Service Managers"),
            "medical health services manager": ("11-9111", "Medical and Health Services Managers"),
            "health administrator": ("11-9111", "Medical and Health Services Managers"),
            "natural sciences manager": ("11-9121", "Natural Sciences Managers"),
            "property manager": ("11-9141", "Property, Real Estate, and Community Association Managers"),
            "social community service manager": ("11-9151", "Social and Community Service Managers"),
            "emergency management director": ("11-9161", "Emergency Management Directors"),

            # Business and Financial Operations (13-0000)
            "claims adjuster": ("13-1031", "Claims Adjusters, Examiners, and Investigators"),
            "compliance officer": ("13-1041", "Compliance Officers"),
            "cost estimator": ("13-1051", "Cost Estimators"),
            "human resources specialist": ("13-1071", "Human Resources Specialists"),
            "hr specialist": ("13-1071", "Human Resources Specialists"),
            "personnel specialist": ("13-1071", "Human Resources Specialists"),
            "labor relations specialist": ("13-1075", "Labor Relations Specialists"),
            "logistician": ("13-1081", "Logisticians"),
            "management analyst": ("13-1111", "Management Analysts"),
            "program analyst": ("13-1111", "Management Analysts"),
            "business analyst": ("13-1111", "Management Analysts"),
            "meeting planner": ("13-1121", "Meeting, Convention, and Event Planners"),
            "event coordinator": ("13-1121", "Meeting, Convention, and Event Planners"),
            "fundraiser": ("13-1131", "Fundraisers"),
            "project manager": ("13-1198", "Project Management Specialists"),
            "training specialist": ("13-1151", "Training and Development Specialists"),
            "accountant": ("13-2011", "Accountants and Auditors"),
            "auditor": ("13-2011", "Accountants and Auditors"),
            "budget analyst": ("13-2031", "Budget Analysts"),
            "credit analyst": ("13-2041", "Credit Analysts"),
            "financial analyst": ("13-2051", "Financial Analysts"),
            "financial examiner": ("13-2061", "Financial Examiners"),
            "loan officer": ("13-2072", "Loan Officers"),
            "tax examiner": ("13-2081", "Tax Examiners and Collectors, and Revenue Agents"),
            "tax collector": ("13-2081", "Tax Examiners and Collectors, and Revenue Agents"),
            "revenue agent": ("13-2081", "Tax Examiners and Collectors, and Revenue Agents"),

            # Computer and Mathematical Occupations (15-0000)
            "computer systems analyst": ("15-1211", "Computer Systems Analysts"),
            "systems analyst": ("15-1211", "Computer Systems Analysts"),
            "information security analyst": ("15-1212", "Information Security Analysts"),
            "cybersecurity analyst": ("15-1212", "Information Security Analysts"),
            "computer programmer": ("15-1251", "Computer Programmers"),
            "programmer": ("15-1251", "Computer Programmers"),
            "software developer": ("15-1252", "Software Developers"),
            "software engineer": ("15-1252", "Software Developers"),
            "web developer": ("15-1254", "Web Developers"),
            "database administrator": ("15-1242", "Database Administrators"),
            "dba": ("15-1242", "Database Administrators"),
            "network administrator": ("15-1244", "Network and Computer Systems Administrators"),
            "systems administrator": ("15-1244", "Network and Computer Systems Administrators"),
            "computer support specialist": ("15-1232", "Computer User Support Specialists"),
            "help desk": ("15-1232", "Computer User Support Specialists"),
            "it support": ("15-1232", "Computer User Support Specialists"),
            "network engineer": ("15-1241", "Computer Network Architects"),
            "data scientist": ("15-2051", "Data Scientists"),
            "statistician": ("15-2041", "Statisticians"),

            # Architecture and Engineering (17-0000)
            "architect": ("17-1011", "Architects, Except Landscape and Naval"),
            "landscape architect": ("17-1012", "Landscape Architects"),
            "surveyor": ("17-1022", "Surveyors"),
            "cartographer": ("17-1021", "Cartographers and Photogrammetrists"),
            "aerospace engineer": ("17-2011", "Aerospace Engineers"),
            "biomedical engineer": ("17-2031", "Biomedical Engineers"),
            "chemical engineer": ("17-2041", "Chemical Engineers"),
            "civil engineer": ("17-2051", "Civil Engineers"),
            "electrical engineer": ("17-2071", "Electrical Engineers"),
            "electronics engineer": ("17-2072", "Electronics Engineers, Except Computer"),
            "environmental engineer": ("17-2081", "Environmental Engineers"),
            "health safety engineer": ("17-2111", "Health and Safety Engineers, Except Mining Safety Engineers and Inspectors"),
            "industrial engineer": ("17-2112", "Industrial Engineers"),
            "mechanical engineer": ("17-2141", "Mechanical Engineers"),
            "engineering technician": ("17-3029", "Engineering Technologists and Technicians, Except Drafters, All Other"),
            "drafter": ("17-3011", "Architectural and Civil Drafters"),
            "cad technician": ("17-3011", "Architectural and Civil Drafters"),
            "surveying technician": ("17-3031", "Surveying and Mapping Technicians"),

            # Life, Physical, and Social Science (19-0000)
            "agricultural scientist": ("19-1011", "Animal Scientists"),
            "food scientist": ("19-1012", "Food Scientists and Technologists"),
            "soil scientist": ("19-1013", "Soil and Plant Scientists"),
            "biochemist": ("19-1021", "Biochemists and Biophysicists"),
            "microbiologist": ("19-1022", "Microbiologists"),
            "zoologist": ("19-1023", "Zoologists and Wildlife Biologists"),
            "wildlife biologist": ("19-1023", "Zoologists and Wildlife Biologists"),
            "conservation scientist": ("19-1031", "Conservation Scientists"),
            "forester": ("19-1032", "Foresters"),
            "epidemiologist": ("19-1041", "Epidemiologists"),
            "medical scientist": ("19-1042", "Medical Scientists, Except Epidemiologists"),
            "chemist": ("19-2031", "Chemists"),
            "environmental scientist": ("19-2041", "Environmental Scientists and Specialists, Including Health"),
            "geoscientist": ("19-2042", "Geoscientists, Except Hydrologists and Geographers"),
            "geologist": ("19-2042", "Geoscientists, Except Hydrologists and Geographers"),
            "hydrologist": ("19-2043", "Hydrologists"),
            "economist": ("19-3011", "Economists"),
            "psychologist": ("19-3031", "Clinical and Counseling Psychologists"),
            "sociologist": ("19-3041", "Sociologists"),
            "urban planner": ("19-3051", "Urban and Regional Planners"),
            "city planner": ("19-3051", "Urban and Regional Planners"),
            "anthropologist": ("19-3091", "Anthropologists and Archeologists"),
            "historian": ("19-3093", "Historians"),
            "political scientist": ("19-3094", "Political Scientists"),
            "chemical technician": ("19-4031", "Chemical Technicians"),
            "environmental science technician": ("19-4042", "Environmental Science and Protection Technicians, Including Health"),
            "forensic science technician": ("19-4092", "Forensic Science Technicians"),

            # Community and Social Service (21-0000)
            "substance abuse counselor": ("21-1011", "Substance Abuse and Behavioral Disorder Counselors"),
            "educational counselor": ("21-1012", "Educational, Guidance, and Career Counselors and Advisors"),
            "guidance counselor": ("21-1012", "Educational, Guidance, and Career Counselors and Advisors"),
            "career counselor": ("21-1012", "Educational, Guidance, and Career Counselors and Advisors"),
            "marriage family therapist": ("21-1013", "Marriage and Family Therapists"),
            "mental health counselor": ("21-1014", "Mental Health Counselors"),
            "rehabilitation counselor": ("21-1015", "Rehabilitation Counselors"),
            "social worker": ("21-1021", "Child, Family, and School Social Workers"),
            "case manager": ("21-1021", "Child, Family, and School Social Workers"),
            "healthcare social worker": ("21-1022", "Healthcare Social Workers"),
            "mental health social worker": ("21-1023", "Mental Health and Substance Abuse Social Workers"),
            "health educator": ("21-1091", "Health Education Specialists"),
            "probation officer": ("21-1092", "Probation Officers and Correctional Treatment Specialists"),
            "parole officer": ("21-1092", "Probation Officers and Correctional Treatment Specialists"),
            "social human service assistant": ("21-1093", "Social and Human Service Assistants"),
            "community health worker": ("21-1094", "Community Health Workers"),
            "eligibility worker": ("43-4061", "Eligibility Interviewers, Government Programs"),
            "clergy": ("21-2011", "Clergy"),
            "chaplain": ("21-2011", "Clergy"),

            # Legal Occupations (23-0000)
            "lawyer": ("23-1011", "Lawyers"),
            "attorney": ("23-1011", "Lawyers"),
            "judge": ("23-1023", "Judges, Magistrate Judges, and Magistrates"),
            "magistrate": ("23-1023", "Judges, Magistrate Judges, and Magistrates"),
            "hearing officer": ("23-1022", "Arbitrators, Mediators, and Conciliators"),
            "paralegal": ("23-2011", "Paralegals and Legal Assistants"),
            "legal assistant": ("23-2011", "Paralegals and Legal Assistants"),
            "court reporter": ("23-2091", "Court Reporters and Simultaneous Captioners"),
            "title examiner": ("23-2093", "Title Examiners, Abstractors, and Searchers"),

            # Education, Training, and Library (25-0000)
            "postsecondary teacher": ("25-1099", "Postsecondary Teachers, All Other"),
            "professor": ("25-1099", "Postsecondary Teachers, All Other"),
            "instructor": ("25-1099", "Postsecondary Teachers, All Other"),
            "preschool teacher": ("25-2011", "Preschool Teachers, Except Special Education"),
            "kindergarten teacher": ("25-2012", "Kindergarten Teachers, Except Special Education"),
            "elementary school teacher": ("25-2021", "Elementary School Teachers, Except Special Education"),
            "middle school teacher": ("25-2022", "Middle School Teachers, Except Special and Career/Technical Education"),
            "high school teacher": ("25-2031", "High School Teachers, Except Special and Career/Technical Education"),
            "special education teacher": ("25-2050", "Special Education Teachers"),
            "adult education teacher": ("25-3011", "Adult Basic Education, Adult Secondary Education, and English as a Second Language Instructors"),
            "librarian": ("25-4022", "Librarians and Media Collections Specialists"),
            "library technician": ("25-4031", "Library Technicians"),
            "archivist": ("25-4011", "Archivists"),
            "curator": ("25-4012", "Curators"),
            "museum technician": ("25-4013", "Museum Technicians and Conservators"),
            "teaching assistant": ("25-9045", "Teaching Assistants, Except Postsecondary"),
            "tutor": ("25-3041", "Tutors"),

            # Arts, Design, Entertainment, Sports, and Media (27-0000)
            "art director": ("27-1011", "Art Directors"),
            "craft artist": ("27-1012", "Craft Artists"),
            "graphic designer": ("27-1024", "Graphic Designers"),
            "interior designer": ("27-1025", "Interior Designers"),
            "photographer": ("27-4021", "Photographers"),
            "camera operator": ("27-4031", "Camera Operators, Television, Video, and Film"),
            "film editor": ("27-4032", "Film and Video Editors"),
            "broadcast technician": ("27-4012", "Broadcast Technicians"),
            "public relations specialist": ("27-3031", "Public Relations Specialists"),
            "writer": ("27-3043", "Writers and Authors"),
            "editor": ("27-3041", "Editors"),
            "technical writer": ("27-3042", "Technical Writers"),
            "interpreter": ("27-3091", "Interpreters and Translators"),
            "translator": ("27-3091", "Interpreters and Translators"),

            # Healthcare Practitioners and Technical (29-0000)
            "dentist": ("29-1021", "Dentists, General"),
            "dietitian": ("29-1031", "Dietitians and Nutritionists"),
            "nutritionist": ("29-1031", "Dietitians and Nutritionists"),
            "pharmacist": ("29-1051", "Pharmacists"),
            "physician": ("29-1216", "General Internal Medicine Physicians"),
            "doctor": ("29-1216", "General Internal Medicine Physicians"),
            "physician assistant": ("29-1071", "Physician Assistants"),
            "registered nurse": ("29-1141", "Registered Nurses"),
            "rn": ("29-1141", "Registered Nurses"),
            "nurse practitioner": ("29-1171", "Nurse Practitioners"),
            "nurse midwife": ("29-1161", "Nurse Midwives"),
            "nurse anesthetist": ("29-1151", "Nurse Anesthetists"),
            "occupational therapist": ("29-1122", "Occupational Therapists"),
            "physical therapist": ("29-1123", "Physical Therapists"),
            "respiratory therapist": ("29-1126", "Respiratory Therapists"),
            "speech pathologist": ("29-1127", "Speech-Language Pathologists"),
            "veterinarian": ("29-1131", "Veterinarians"),
            "clinical laboratory technologist": ("29-2011", "Medical and Clinical Laboratory Technologists"),
            "medical technologist": ("29-2011", "Medical and Clinical Laboratory Technologists"),
            "dental hygienist": ("29-1292", "Dental Hygienists"),
            "cardiovascular technologist": ("29-2031", "Cardiovascular Technologists and Technicians"),
            "diagnostic medical sonographer": ("29-2032", "Diagnostic Medical Sonographers"),
            "radiologic technologist": ("29-2034", "Radiologic Technologists and Technicians"),
            "emt": ("29-2041", "Emergency Medical Technicians"),
            "paramedic": ("29-2043", "Paramedics"),
            "pharmacy technician": ("29-2052", "Pharmacy Technicians"),
            "psychiatric technician": ("29-2053", "Psychiatric Technicians"),
            "surgical technologist": ("29-2055", "Surgical Technologists"),
            "veterinary technologist": ("29-2056", "Veterinary Technologists and Technicians"),
            "licensed practical nurse": ("29-2061", "Licensed Practical and Licensed Vocational Nurses"),
            "lpn": ("29-2061", "Licensed Practical and Licensed Vocational Nurses"),
            "optician": ("29-2081", "Opticians, Dispensing"),
            "health technologist": ("29-2099", "Health Technologists and Technicians, All Other"),
            "medical records technician": ("29-2072", "Medical Records Specialists"),
            "health information technician": ("29-2072", "Medical Records Specialists"),

            # Healthcare Support (31-0000)
            "home health aide": ("31-1121", "Home Health Aides"),
            "nursing assistant": ("31-1131", "Nursing Assistants"),
            "cna": ("31-1131", "Nursing Assistants"),
            "orderly": ("31-1132", "Orderlies"),
            "psychiatric aide": ("31-1133", "Psychiatric Aides"),
            "occupational therapy assistant": ("31-2011", "Occupational Therapy Assistants"),
            "physical therapist assistant": ("31-2021", "Physical Therapist Assistants"),
            "massage therapist": ("31-9011", "Massage Therapists"),
            "dental assistant": ("31-9091", "Dental Assistants"),
            "medical assistant": ("31-9092", "Medical Assistants"),
            "phlebotomist": ("31-9097", "Phlebotomists"),

            # Protective Service (33-0000)
            "first line supervisor police": ("33-1012", "First-Line Supervisors of Police and Detectives"),
            "police sergeant": ("33-1012", "First-Line Supervisors of Police and Detectives"),
            "police lieutenant": ("33-1012", "First-Line Supervisors of Police and Detectives"),
            "fire chief": ("33-1021", "First-Line Supervisors of Firefighting and Prevention Workers"),
            "fire captain": ("33-1021", "First-Line Supervisors of Firefighting and Prevention Workers"),
            "correctional officer supervisor": ("33-1011", "First-Line Supervisors of Correctional Officers"),
            "firefighter": ("33-2011", "Firefighters"),
            "fire inspector": ("33-2021", "Fire Inspectors and Investigators"),
            "forest fire inspector": ("33-2022", "Forest Fire Inspectors and Prevention Specialists"),
            "bailiff": ("33-3011", "Bailiffs"),
            "correctional officer": ("33-3012", "Correctional Officers and Jailers"),
            "jailer": ("33-3012", "Correctional Officers and Jailers"),
            "detective": ("33-3021", "Detectives and Criminal Investigators"),
            "criminal investigator": ("33-3021", "Detectives and Criminal Investigators"),
            "fish game warden": ("33-3031", "Fish and Game Wardens"),
            "conservation officer": ("33-3031", "Fish and Game Wardens"),
            "parking enforcement": ("33-3041", "Parking Enforcement Workers"),
            "police officer": ("33-3051", "Police and Sheriff's Patrol Officers"),
            "sheriff": ("33-3051", "Police and Sheriff's Patrol Officers"),
            "deputy sheriff": ("33-3051", "Police and Sheriff's Patrol Officers"),
            "trooper": ("33-3051", "Police and Sheriff's Patrol Officers"),
            "transit police": ("33-3052", "Transit and Railroad Police"),
            "animal control worker": ("33-9011", "Animal Control Workers"),
            "private detective": ("33-9021", "Private Detectives and Investigators"),
            "security guard": ("33-9032", "Security Guards"),
            "crossing guard": ("33-9091", "Crossing Guards and Flaggers"),
            "lifeguard": ("33-9092", "Lifeguards, Ski Patrol, and Other Recreational Protective Service Workers"),
            "tsa officer": ("33-9093", "Transportation Security Screeners"),

            # Food Preparation and Serving (35-0000)
            "chef": ("35-1011", "Chefs and Head Cooks"),
            "head cook": ("35-1011", "Chefs and Head Cooks"),
            "food service supervisor": ("35-1012", "First-Line Supervisors of Food Preparation and Serving Workers"),
            "cook": ("35-2014", "Cooks, Restaurant"),
            "food preparation worker": ("35-2021", "Food Preparation Workers"),
            "bartender": ("35-3011", "Bartenders"),
            "food server": ("35-3041", "Food Servers, Nonrestaurant"),
            "waiter": ("35-3031", "Waiters and Waitresses"),
            "waitress": ("35-3031", "Waiters and Waitresses"),
            "dishwasher": ("35-9021", "Dishwashers"),

            # Building and Grounds Cleaning and Maintenance (37-0000)
            "housekeeping supervisor": ("37-1011", "First-Line Supervisors of Housekeeping and Janitorial Workers"),
            "landscaping supervisor": ("37-1012", "First-Line Supervisors of Landscaping, Lawn Service, and Groundskeeping Workers"),
            "janitor": ("37-2011", "Janitors and Cleaners, Except Maids and Housekeeping Cleaners"),
            "custodian": ("37-2011", "Janitors and Cleaners, Except Maids and Housekeeping Cleaners"),
            "cleaner": ("37-2011", "Janitors and Cleaners, Except Maids and Housekeeping Cleaners"),
            "maid": ("37-2012", "Maids and Housekeeping Cleaners"),
            "housekeeper": ("37-2012", "Maids and Housekeeping Cleaners"),
            "pest control worker": ("37-2021", "Pest Control Workers"),
            "landscaper": ("37-3011", "Landscaping and Groundskeeping Workers"),
            "groundskeeper": ("37-3011", "Landscaping and Groundskeeping Workers"),
            "tree trimmer": ("37-3013", "Tree Trimmers and Pruners"),

            # Personal Care and Service (39-0000)
            "gaming supervisor": ("39-1013", "First-Line Supervisors of Gambling Services Workers"),
            "animal trainer": ("39-2011", "Animal Trainers"),
            "animal caretaker": ("39-2021", "Animal Caretakers"),
            "barber": ("39-5011", "Barbers"),
            "hairdresser": ("39-5012", "Hairdressers, Hairstylists, and Cosmetologists"),
            "recreation worker": ("39-9032", "Recreation Workers"),
            "tour guide": ("39-7011", "Tour Guides and Escorts"),
            "childcare worker": ("39-9011", "Childcare Workers"),
            "personal care aide": ("39-9021", "Personal Care Aides"),
            "fitness trainer": ("39-9031", "Fitness Trainers and Aerobics Instructors"),

            # Sales and Related (41-0000)
            "sales supervisor": ("41-1011", "First-Line Supervisors of Retail Sales Workers"),
            "cashier": ("41-2011", "Cashiers"),
            "retail salesperson": ("41-2031", "Retail Salespersons"),
            "parts salesperson": ("41-2022", "Parts Salespersons"),
            "insurance sales agent": ("41-3021", "Insurance Sales Agents"),
            "real estate agent": ("41-9022", "Real Estate Sales Agents"),
            "sales representative": ("41-4012", "Sales Representatives, Wholesale and Manufacturing, Except Technical and Scientific Products"),

            # Office and Administrative Support (43-0000)
            "administrative supervisor": ("43-1011", "First-Line Supervisors of Office and Administrative Support Workers"),
            "office supervisor": ("43-1011", "First-Line Supervisors of Office and Administrative Support Workers"),
            "bill collector": ("43-3011", "Bill and Account Collectors"),
            "billing clerk": ("43-3021", "Billing and Posting Clerks"),
            "bookkeeper": ("43-3031", "Bookkeeping, Accounting, and Auditing Clerks"),
            "accounting clerk": ("43-3031", "Bookkeeping, Accounting, and Auditing Clerks"),
            "gaming cage worker": ("43-3041", "Gambling Cage Workers"),
            "payroll clerk": ("43-3051", "Payroll and Timekeeping Clerks"),
            "procurement clerk": ("43-3061", "Procurement Clerks"),
            "teller": ("43-3071", "Tellers"),
            "brokerage clerk": ("43-4011", "Brokerage Clerks"),
            "correspondence clerk": ("43-4021", "Correspondence Clerks"),
            "court clerk": ("43-4031", "Court, Municipal, and License Clerks"),
            "license clerk": ("43-4031", "Court, Municipal, and License Clerks"),
            "municipal clerk": ("43-4031", "Court, Municipal, and License Clerks"),
            "credit authorizer": ("43-4041", "Credit Authorizers, Checkers, and Clerks"),
            "customer service representative": ("43-4051", "Customer Service Representatives"),
            "eligibility interviewer": ("43-4061", "Eligibility Interviewers, Government Programs"),
            "file clerk": ("43-4071", "File Clerks"),
            "hotel desk clerk": ("43-4081", "Hotel, Motel, and Resort Desk Clerks"),
            "interviewer": ("43-4111", "Interviewers, Except Eligibility and Loan"),
            "library assistant": ("43-4121", "Library Assistants, Clerical"),
            "loan interviewer": ("43-4131", "Loan Interviewers and Clerks"),
            "new accounts clerk": ("43-4141", "New Accounts Clerks"),
            "order clerk": ("43-4151", "Order Clerks"),
            "human resources assistant": ("43-4161", "Human Resources Assistants, Except Payroll and Timekeeping"),
            "hr assistant": ("43-4161", "Human Resources Assistants, Except Payroll and Timekeeping"),
            "receptionist": ("43-4171", "Receptionists and Information Clerks"),
            "information clerk": ("43-4171", "Receptionists and Information Clerks"),
            "reservation agent": ("43-4181", "Reservation and Transportation Ticket Agents and Travel Clerks"),
            "cargo agent": ("43-5011", "Cargo and Freight Agents"),
            "courier": ("43-5021", "Couriers and Messengers"),
            "dispatcher": ("43-5032", "Dispatchers, Except Police, Fire, and Ambulance"),
            "police dispatcher": ("43-5031", "Public Safety Telecommunicators"),
            "911 operator": ("43-5031", "Public Safety Telecommunicators"),
            "meter reader": ("43-5041", "Meter Readers, Utilities"),
            "postal service clerk": ("43-5051", "Postal Service Clerks"),
            "mail carrier": ("43-5052", "Postal Service Mail Carriers"),
            "mail sorter": ("43-5053", "Postal Service Mail Sorters, Processors, and Processing Machine Operators"),
            "shipping clerk": ("43-5071", "Shipping, Receiving, and Inventory Clerks"),
            "stock clerk": ("43-5081", "Stock Clerks and Order Fillers"),
            "weigher": ("43-5111", "Weighers, Measurers, Checkers, and Samplers, Recordkeeping"),
            "executive secretary": ("43-6011", "Executive Secretaries and Executive Administrative Assistants"),
            "executive assistant": ("43-6011", "Executive Secretaries and Executive Administrative Assistants"),
            "legal secretary": ("43-6012", "Legal Secretaries and Administrative Assistants"),
            "medical secretary": ("43-6013", "Medical Secretaries and Administrative Assistants"),
            "secretary": ("43-6014", "Secretaries and Administrative Assistants, Except Legal, Medical, and Executive"),
            "administrative assistant": ("43-6014", "Secretaries and Administrative Assistants, Except Legal, Medical, and Executive"),
            "data entry keyer": ("43-9021", "Data Entry Keyers"),
            "word processor": ("43-9022", "Word Processors and Typists"),
            "typist": ("43-9022", "Word Processors and Typists"),
            "office clerk": ("43-9061", "Office Clerks, General"),
            "general clerk": ("43-9061", "Office Clerks, General"),

            # Farming, Fishing, and Forestry (45-0000)
            "agricultural inspector": ("45-2011", "Agricultural Inspectors"),
            "farm worker": ("45-2092", "Farmworkers and Laborers, Crop, Nursery, and Greenhouse"),
            "forest worker": ("45-4011", "Forest and Conservation Workers"),
            "logging worker": ("45-4021", "Fallers"),

            # Construction and Extraction (47-0000)
            "construction supervisor": ("47-1011", "First-Line Supervisors of Construction Trades and Extraction Workers"),
            "boilermaker": ("47-2011", "Boilermakers"),
            "brickmason": ("47-2021", "Brickmasons and Blockmasons"),
            "carpenter": ("47-2031", "Carpenters"),
            "carpet installer": ("47-2041", "Carpet Installers"),
            "cement mason": ("47-2051", "Cement Masons and Concrete Finishers"),
            "construction laborer": ("47-2061", "Construction Laborers"),
            "paving equipment operator": ("47-2071", "Paving, Surfacing, and Tamping Equipment Operators"),
            "operating engineer": ("47-2073", "Operating Engineers and Other Construction Equipment Operators"),
            "heavy equipment operator": ("47-2073", "Operating Engineers and Other Construction Equipment Operators"),
            "drywall installer": ("47-2081", "Drywall and Ceiling Tile Installers"),
            "electrician": ("47-2111", "Electricians"),
            "glazier": ("47-2121", "Glaziers"),
            "insulation worker": ("47-2131", "Insulation Workers, Floor, Ceiling, and Wall"),
            "painter": ("47-2141", "Painters, Construction and Maintenance"),
            "pipelayer": ("47-2151", "Pipelayers"),
            "plumber": ("47-2152", "Plumbers, Pipefitters, and Steamfitters"),
            "pipefitter": ("47-2152", "Plumbers, Pipefitters, and Steamfitters"),
            "roofer": ("47-2181", "Roofers"),
            "sheet metal worker": ("47-2211", "Sheet Metal Workers"),
            "structural iron worker": ("47-2221", "Structural Iron and Steel Workers"),
            "highway maintenance worker": ("47-4051", "Highway Maintenance Workers"),
            "septic tank servicer": ("47-4071", "Septic Tank Servicers and Sewer Pipe Cleaners"),

            # Installation, Maintenance, and Repair (49-0000)
            "maintenance supervisor": ("49-1011", "First-Line Supervisors of Mechanics, Installers, and Repairers"),
            "computer repairer": ("49-2011", "Computer, Automated Teller, and Office Machine Repairers"),
            "radio mechanic": ("49-2021", "Radio, Cellular, and Tower Equipment Installers and Repairers"),
            "telecommunications installer": ("49-2022", "Telecommunications Equipment Installers and Repairers, Except Line Installers"),
            "avionics technician": ("49-2091", "Avionics Technicians"),
            "electric motor repairer": ("49-2092", "Electric Motor, Power Tool, and Related Repairers"),
            "electrical repairer": ("49-2093", "Electrical and Electronics Installers and Repairers, Transportation Equipment"),
            "powerhouse electrician": ("49-2095", "Electrical and Electronics Repairers, Powerhouse, Substation, and Relay"),
            "electronic equipment repairer": ("49-2097", "Audiovisual Equipment Installers and Repairers"),
            "security alarm installer": ("49-2098", "Security and Fire Alarm Systems Installers"),
            "aircraft mechanic": ("49-3011", "Aircraft Mechanics and Service Technicians"),
            "automotive body repairer": ("49-3021", "Automotive Body and Related Repairers"),
            "automotive technician": ("49-3023", "Automotive Service Technicians and Mechanics"),
            "auto mechanic": ("49-3023", "Automotive Service Technicians and Mechanics"),
            "bus mechanic": ("49-3031", "Bus and Truck Mechanics and Diesel Engine Specialists"),
            "diesel mechanic": ("49-3031", "Bus and Truck Mechanics and Diesel Engine Specialists"),
            "truck mechanic": ("49-3031", "Bus and Truck Mechanics and Diesel Engine Specialists"),
            "farm equipment mechanic": ("49-3041", "Farm Equipment Mechanics and Service Technicians"),
            "mobile equipment mechanic": ("49-3042", "Mobile Heavy Equipment Mechanics, Except Engines"),
            "rail car repairer": ("49-3043", "Rail Car Repairers"),
            "motorboat mechanic": ("49-3051", "Motorboat Mechanics and Service Technicians"),
            "motorcycle mechanic": ("49-3052", "Motorcycle Mechanics"),
            "outdoor power equipment mechanic": ("49-3053", "Outdoor Power Equipment and Other Small Engine Mechanics"),
            "bicycle repairer": ("49-3091", "Bicycle Repairers"),
            "tire repairer": ("49-3093", "Tire Repairers and Changers"),
            "heating technician": ("49-9021", "Heating, Air Conditioning, and Refrigeration Mechanics and Installers"),
            "hvac technician": ("49-9021", "Heating, Air Conditioning, and Refrigeration Mechanics and Installers"),
            "home appliance repairer": ("49-9031", "Home Appliance Repairers"),
            "industrial machinery mechanic": ("49-9041", "Industrial Machinery Mechanics"),
            "maintenance worker": ("49-9071", "Maintenance and Repair Workers, General"),
            "building maintenance": ("49-9071", "Maintenance and Repair Workers, General"),
            "millwright": ("49-9044", "Millwrights"),
            "electrical line installer": ("49-9051", "Electrical Power-Line Installers and Repairers"),
            "lineman": ("49-9051", "Electrical Power-Line Installers and Repairers"),
            "telecommunications line installer": ("49-9052", "Telecommunications Line Installers and Repairers"),
            "locksmith": ("49-9094", "Locksmiths and Safe Repairers"),
            "signal repairer": ("49-9097", "Signal and Track Switch Repairers"),

            # Production Occupations (51-0000)
            "production supervisor": ("51-1011", "First-Line Supervisors of Production and Operating Workers"),
            "assembler": ("51-2098", "Miscellaneous Assemblers and Fabricators"),
            "baker": ("51-3011", "Bakers"),
            "butcher": ("51-3021", "Butchers and Meat Cutters"),
            "laundry worker": ("51-6011", "Laundry and Dry-Cleaning Workers"),
            "presser": ("51-6021", "Pressers, Textile, Garment, and Related Materials"),
            "sewing machine operator": ("51-6031", "Sewing Machine Operators"),
            "tailor": ("51-6052", "Tailors, Dressmakers, and Custom Sewers"),
            "cabinetmaker": ("51-7011", "Cabinetmakers and Bench Carpenters"),
            "sawing machine operator": ("51-7041", "Sawing Machine Setters, Operators, and Tenders, Wood"),
            "woodworker": ("51-7099", "Woodworkers, All Other"),
            "power plant operator": ("51-8013", "Power Plant Operators"),
            "boiler operator": ("51-8021", "Stationary Engineers and Boiler Operators"),
            "water treatment operator": ("51-8031", "Water and Wastewater Treatment Plant and System Operators"),
            "chemical plant operator": ("51-8091", "Chemical Plant and System Operators"),
            "gas plant operator": ("51-8092", "Gas Plant Operators"),
            "petroleum pump operator": ("51-8093", "Petroleum Pump System Operators, Refinery Operators, and Gaugers"),
            "machinist": ("51-4041", "Machinists"),
            "tool die maker": ("51-4111", "Tool and Die Makers"),
            "welder": ("51-4121", "Welders, Cutters, Solderers, and Brazers"),
            "printing press operator": ("51-5112", "Printing Press Operators"),
            "print binding worker": ("51-5113", "Print Binding and Finishing Workers"),
            "inspector": ("51-9061", "Inspectors, Testers, Sorters, Samplers, and Weighers"),
            "quality control inspector": ("51-9061", "Inspectors, Testers, Sorters, Samplers, and Weighers"),
            "packaging machine operator": ("51-9111", "Packaging and Filling Machine Operators and Tenders"),
            "painting worker": ("51-9124", "Coating, Painting, and Spraying Machine Setters, Operators, and Tenders"),

            # Transportation and Material Moving (53-0000)
            "transportation supervisor": ("53-1047", "First-Line Supervisors of Transportation and Material Moving Workers, Except Aircraft Cargo Handling Supervisors"),
            "aircraft cargo supervisor": ("53-1041", "Aircraft Cargo Handling Supervisors"),
            "airline pilot": ("53-2011", "Airline Pilots, Copilots, and Flight Engineers"),
            "commercial pilot": ("53-2012", "Commercial Pilots"),
            "air traffic controller": ("53-2021", "Air Traffic Controllers"),
            "flight attendant": ("53-2031", "Flight Attendants"),
            "ambulance driver": ("53-3011", "Ambulance Drivers and Attendants, Except Emergency Medical Technicians"),
            "bus driver": ("53-3021", "Bus Drivers, Transit and Intercity"),
            "school bus driver": ("53-3022", "Bus Drivers, School"),
            "delivery driver": ("53-3031", "Driver/Sales Workers"),
            "heavy truck driver": ("53-3032", "Heavy and Tractor-Trailer Truck Drivers"),
            "truck driver": ("53-3032", "Heavy and Tractor-Trailer Truck Drivers"),
            "light truck driver": ("53-3033", "Light Truck Drivers"),
            "taxi driver": ("53-3041", "Taxi Drivers"),
            "motor vehicle operator": ("53-3099", "Motor Vehicle Operators, All Other"),
            "locomotive engineer": ("53-4011", "Locomotive Engineers"),
            "rail yard engineer": ("53-4013", "Rail Yard Engineers, Dinkey Operators, and Hostlers"),
            "railroad conductor": ("53-4031", "Railroad Conductors and Yardmasters"),
            "subway operator": ("53-4041", "Subway and Streetcar Operators"),
            "sailor": ("53-5011", "Sailors and Marine Oilers"),
            "ship captain": ("53-5021", "Captains, Mates, and Pilots of Water Vessels"),
            "ship engineer": ("53-5031", "Ship Engineers"),
            "bridge tender": ("53-6011", "Bridge and Lock Tenders"),
            "parking attendant": ("53-6021", "Parking Attendants"),
            "automotive detailer": ("53-7061", "Cleaners of Vehicles and Equipment"),
            "crane operator": ("53-7021", "Crane and Tower Operators"),
            "excavating operator": ("53-7032", "Excavating and Loading Machine and Dragline Operators, Surface Mining"),
            "industrial truck operator": ("53-7051", "Industrial Truck and Tractor Operators"),
            "forklift operator": ("53-7051", "Industrial Truck and Tractor Operators"),
            "laborer": ("53-7062", "Laborers and Freight, Stock, and Material Movers, Hand"),
            "material mover": ("53-7062", "Laborers and Freight, Stock, and Material Movers, Hand"),
            "machine feeder": ("53-7063", "Machine Feeders and Offbearers"),
            "refuse collector": ("53-7081", "Refuse and Recyclable Material Collectors"),
            "garbage collector": ("53-7081", "Refuse and Recyclable Material Collectors"),
            "tank car loader": ("53-7121", "Tank Car, Truck, and Ship Loaders"),
        }

    def find_soc_code(self, job_title: str) -> Tuple[str, str]:
        """
        Find the best matching SOC code for a job title

        Args:
            job_title: The job title to match

        Returns:
            Tuple of (SOC code, SOC title) or ("", "") if no match
        """
        if not job_title:
            return ("", "")

        job_title_lower = job_title.lower()

        # Direct match first
        for keyword, (code, title) in self.soc_database.items():
            if keyword in job_title_lower:
                return (code, title)

        # Try partial matching with word boundaries
        job_words = set(job_title_lower.split())
        best_match = None
        best_score = 0

        for keyword, (code, title) in self.soc_database.items():
            keyword_words = set(keyword.split())
            overlap = len(job_words & keyword_words)
            if overlap > best_score:
                best_score = overlap
                best_match = (code, title)

        if best_match and best_score >= 1:
            return best_match

        return ("", "")


class JobClassificationScraper:
    """
    Web scraper for extracting job classification data from government job portals
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.soc_mapper = SOCCodeMapper()
        self.classifications = []

    def _generate_abbreviation(self, job_title: str) -> str:
        """Generate job title abbreviation from full title"""
        # Common abbreviation rules
        abbreviations = {
            "Administrative": "Admin",
            "Administrator": "Admin",
            "Assistant": "Asst",
            "Associate": "Assoc",
            "Coordinator": "Coord",
            "Department": "Dept",
            "Development": "Dev",
            "Director": "Dir",
            "Engineer": "Engr",
            "Environmental": "Environ",
            "Information": "Info",
            "Inspector": "Insp",
            "Laboratory": "Lab",
            "Lieutenant": "Lt",
            "Maintenance": "Maint",
            "Management": "Mgmt",
            "Manager": "Mgr",
            "Mechanical": "Mech",
            "Officer": "Ofcr",
            "Operations": "Ops",
            "Professional": "Prof",
            "Programmer": "Prgmr",
            "Representative": "Rep",
            "Secretary": "Secy",
            "Sergeant": "Sgt",
            "Services": "Svcs",
            "Specialist": "Spec",
            "Supervisor": "Supv",
            "Technical": "Tech",
            "Technician": "Tech",
            "Technology": "Tech",
            "Transportation": "Trans",
        }

        abbrev = job_title
        for full, short in abbreviations.items():
            abbrev = abbrev.replace(full, short)

        # Truncate if still too long
        if len(abbrev) > 25:
            words = abbrev.split()
            abbrev = " ".join(w[:4] if len(w) > 4 else w for w in words)

        return abbrev[:25]

    def _get_eeo_category(self, soc_code: str) -> str:
        """Get EEO category based on SOC code prefix"""
        if soc_code and len(soc_code) >= 2:
            prefix = soc_code[:2]
            return EEO_CATEGORIES.get(prefix, "Unclassified")
        return "Unclassified"

    def _get_work_level(self, job_title: str) -> str:
        """Determine work level from job title"""
        for keyword, level in WORK_LEVELS.items():
            if keyword in job_title:
                return level
        return "Professional"

    def _get_supervision_received(self, job_title: str) -> str:
        """Determine supervision level from job title"""
        for keyword, supervision in SUPERVISION_LEVELS.items():
            if keyword in job_title:
                return supervision
        return "Moderate - Regular supervision with some independence"

    def _get_work_function(self, soc_code: str, soc_title: str) -> str:
        """Generate work function description from SOC info"""
        if not soc_title:
            return ""

        # Map SOC major groups to work functions
        work_functions = {
            "11": "Management and oversight of organizational operations, staff, and resources",
            "13": "Business operations analysis, financial management, and administrative functions",
            "15": "Computer systems design, programming, data analysis, and technical support",
            "17": "Engineering design, analysis, technical planning, and project oversight",
            "19": "Scientific research, analysis, environmental monitoring, and technical studies",
            "21": "Community services, counseling, case management, and social support",
            "23": "Legal analysis, representation, court administration, and compliance",
            "25": "Education, instruction, library services, and training delivery",
            "27": "Communications, media production, design, and public relations",
            "29": "Healthcare delivery, patient care, medical diagnostics, and treatment",
            "31": "Healthcare support, patient assistance, and clinical support services",
            "33": "Public safety, law enforcement, emergency response, and protective services",
            "35": "Food preparation, service, and hospitality operations",
            "37": "Building maintenance, grounds keeping, and facility operations",
            "39": "Personal care, recreation services, and customer assistance",
            "41": "Sales, customer service, and retail operations",
            "43": "Administrative support, records management, and office operations",
            "45": "Agricultural operations, farming, and natural resource management",
            "47": "Construction, building trades, and infrastructure maintenance",
            "49": "Equipment maintenance, repair, and installation services",
            "51": "Production operations, manufacturing, and quality control",
            "53": "Transportation, material handling, and logistics operations",
        }

        if soc_code and len(soc_code) >= 2:
            prefix = soc_code[:2]
            return work_functions.get(prefix, f"Performs duties related to {soc_title}")

        return f"Performs duties related to {soc_title}"

    def scrape_governmentjobs(self, state: str = "wv", max_pages: int = 50) -> List[JobClassification]:
        """
        Scrape job classifications from governmentjobs.com

        Args:
            state: State abbreviation (e.g., 'wv' for West Virginia)
            max_pages: Maximum number of pages to scrape

        Returns:
            List of JobClassification objects
        """
        base_url = f"https://www.governmentjobs.com/careers/{state}/classspecs"
        classifications = []
        page = 1

        logger.info(f"Starting scrape of {base_url}")

        while page <= max_pages:
            try:
                url = f"{base_url}?page={page}" if page > 1 else base_url
                logger.info(f"Fetching page {page}: {url}")

                response = self.session.get(url, timeout=30)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find job classification listings
                job_items = soup.find_all('tr', class_='job-listing') or \
                           soup.find_all('div', class_='job-listing') or \
                           soup.find_all('li', class_='job-listing')

                if not job_items:
                    # Try alternative selectors
                    job_items = soup.select('table.search-results tr[data-job-id]') or \
                               soup.select('.search-results-item') or \
                               soup.select('[class*="job"]')

                if not job_items:
                    logger.info(f"No more job listings found on page {page}")
                    break

                for item in job_items:
                    classification = self._parse_job_item(item, base_url)
                    if classification:
                        classifications.append(classification)

                # Check for next page
                next_button = soup.find('a', {'aria-label': 'Next'}) or \
                             soup.find('a', text=re.compile(r'next', re.I)) or \
                             soup.find('a', class_='next')

                if not next_button:
                    break

                page += 1
                time.sleep(1)  # Rate limiting

            except requests.RequestException as e:
                logger.error(f"Error fetching page {page}: {e}")
                break

        self.classifications = classifications
        return classifications

    def _parse_job_item(self, item, base_url: str) -> Optional[JobClassification]:
        """Parse a single job item from the page"""
        try:
            # Extract title
            title_elem = item.find('a', class_='job-title') or \
                        item.find('a') or \
                        item.find('td', class_='title')

            if not title_elem:
                return None

            job_title = title_elem.get_text(strip=True)
            job_url = title_elem.get('href', '')
            if job_url and not job_url.startswith('http'):
                job_url = urljoin(base_url, job_url)

            # Extract class code
            code_elem = item.find('td', class_='code') or \
                       item.find('span', class_='class-code')
            class_code = code_elem.get_text(strip=True) if code_elem else ""

            # Extract salary
            salary_elem = item.find('td', class_='salary') or \
                         item.find('span', class_='salary')
            salary = salary_elem.get_text(strip=True) if salary_elem else ""

            # Extract department/category
            dept_elem = item.find('td', class_='department') or \
                       item.find('span', class_='department')
            department = dept_elem.get_text(strip=True) if dept_elem else ""

            # Map to SOC code
            soc_code, soc_title = self.soc_mapper.find_soc_code(job_title)

            return JobClassification(
                job_title=job_title,
                class_code=class_code,
                soc_code=soc_code,
                soc_title=soc_title,
                salary_range=salary,
                department=department,
                category="",
                description="",
                source_url=job_url
            )

        except Exception as e:
            logger.warning(f"Error parsing job item: {e}")
            return None

    def load_from_sample_data(self) -> List[JobClassification]:
        """
        Load sample West Virginia job classification data
        Based on typical state government job classifications
        Output format matches standardized intake spreadsheet
        """
        # Raw data: (job_title, class_code, soc_code, soc_title)
        sample_data = [
            # Administrative and Management
            ("Administrative Secretary", "0101", "43-6014", "Secretaries and Administrative Assistants"),
            ("Administrative Services Manager", "0102", "11-3012", "Administrative Services Managers"),
            ("Administrative Analyst", "0103", "13-1111", "Management Analysts"),
            ("Administrative Assistant", "0104", "43-6014", "Secretaries and Administrative Assistants"),
            ("Agency Director", "0110", "11-1021", "General and Operations Managers"),

            # Accounting and Finance
            ("Accountant I", "0201", "13-2011", "Accountants and Auditors"),
            ("Accountant II", "0202", "13-2011", "Accountants and Auditors"),
            ("Accountant III", "0203", "13-2011", "Accountants and Auditors"),
            ("Accountant Supervisor", "0204", "11-3031", "Financial Managers"),
            ("Accounting Technician", "0205", "43-3031", "Bookkeeping, Accounting, and Auditing Clerks"),
            ("Auditor I", "0210", "13-2011", "Accountants and Auditors"),
            ("Auditor II", "0211", "13-2011", "Accountants and Auditors"),
            ("Auditor III", "0212", "13-2011", "Accountants and Auditors"),
            ("Budget Analyst I", "0220", "13-2031", "Budget Analysts"),
            ("Budget Analyst II", "0221", "13-2031", "Budget Analysts"),
            ("Budget Director", "0222", "11-3031", "Financial Managers"),
            ("Financial Examiner", "0230", "13-2061", "Financial Examiners"),
            ("Fiscal Officer", "0231", "11-3031", "Financial Managers"),
            ("Revenue Agent", "0240", "13-2081", "Tax Examiners and Collectors"),
            ("Tax Examiner", "0241", "13-2081", "Tax Examiners and Collectors"),

            # Information Technology
            ("Computer Operator", "0301", "43-9011", "Computer Operators"),
            ("Computer Programmer I", "0302", "15-1251", "Computer Programmers"),
            ("Computer Programmer II", "0303", "15-1251", "Computer Programmers"),
            ("Computer Programmer III", "0304", "15-1251", "Computer Programmers"),
            ("Database Administrator", "0310", "15-1242", "Database Administrators"),
            ("IT Manager", "0315", "11-3021", "Computer and Information Systems Managers"),
            ("IT Project Manager", "0316", "13-1198", "Project Management Specialists"),
            ("IT Security Analyst", "0317", "15-1212", "Information Security Analysts"),
            ("IT Support Specialist", "0318", "15-1232", "Computer User Support Specialists"),
            ("Network Administrator", "0320", "15-1244", "Network and Computer Systems Administrators"),
            ("Network Engineer", "0321", "15-1241", "Computer Network Architects"),
            ("Software Developer I", "0325", "15-1252", "Software Developers"),
            ("Software Developer II", "0326", "15-1252", "Software Developers"),
            ("Software Developer III", "0327", "15-1252", "Software Developers"),
            ("Systems Analyst I", "0330", "15-1211", "Computer Systems Analysts"),
            ("Systems Analyst II", "0331", "15-1211", "Computer Systems Analysts"),
            ("Systems Analyst III", "0332", "15-1211", "Computer Systems Analysts"),
            ("Web Developer", "0340", "15-1254", "Web Developers"),

            # Engineering
            ("Civil Engineer I", "0401", "17-2051", "Civil Engineers"),
            ("Civil Engineer II", "0402", "17-2051", "Civil Engineers"),
            ("Civil Engineer III", "0403", "17-2051", "Civil Engineers"),
            ("Electrical Engineer I", "0410", "17-2071", "Electrical Engineers"),
            ("Electrical Engineer II", "0411", "17-2071", "Electrical Engineers"),
            ("Engineering Technician I", "0420", "17-3029", "Engineering Technicians"),
            ("Engineering Technician II", "0421", "17-3029", "Engineering Technicians"),
            ("Environmental Engineer I", "0430", "17-2081", "Environmental Engineers"),
            ("Environmental Engineer II", "0431", "17-2081", "Environmental Engineers"),
            ("Highway Engineer", "0440", "17-2051", "Civil Engineers"),
            ("Mechanical Engineer I", "0450", "17-2141", "Mechanical Engineers"),
            ("Mechanical Engineer II", "0451", "17-2141", "Mechanical Engineers"),
            ("Surveyor", "0460", "17-1022", "Surveyors"),
            ("Survey Technician", "0461", "17-3031", "Surveying and Mapping Technicians"),

            # Healthcare
            ("Certified Nursing Assistant", "0501", "31-1131", "Nursing Assistants"),
            ("Clinical Social Worker", "0502", "21-1023", "Mental Health and Substance Abuse Social Workers"),
            ("Dentist", "0503", "29-1021", "Dentists, General"),
            ("Dietitian", "0504", "29-1031", "Dietitians and Nutritionists"),
            ("Health Administrator", "0505", "11-9111", "Medical and Health Services Managers"),
            ("Health Educator", "0506", "21-1091", "Health Education Specialists"),
            ("Health Program Manager", "0507", "11-9111", "Medical and Health Services Managers"),
            ("Laboratory Technician", "0510", "29-2011", "Medical and Clinical Laboratory Technologists"),
            ("Licensed Practical Nurse", "0515", "29-2061", "Licensed Practical Nurses"),
            ("Medical Records Technician", "0516", "29-2072", "Medical Records Specialists"),
            ("Mental Health Counselor", "0520", "21-1014", "Mental Health Counselors"),
            ("Nurse Practitioner", "0525", "29-1171", "Nurse Practitioners"),
            ("Pharmacist", "0530", "29-1051", "Pharmacists"),
            ("Pharmacy Technician", "0531", "29-2052", "Pharmacy Technicians"),
            ("Physical Therapist", "0535", "29-1123", "Physical Therapists"),
            ("Physical Therapy Assistant", "0536", "31-2021", "Physical Therapist Assistants"),
            ("Physician", "0540", "29-1216", "General Internal Medicine Physicians"),
            ("Physician Assistant", "0541", "29-1071", "Physician Assistants"),
            ("Psychologist", "0545", "19-3031", "Clinical and Counseling Psychologists"),
            ("Public Health Nurse", "0550", "29-1141", "Registered Nurses"),
            ("Registered Nurse I", "0551", "29-1141", "Registered Nurses"),
            ("Registered Nurse II", "0552", "29-1141", "Registered Nurses"),
            ("Registered Nurse III", "0553", "29-1141", "Registered Nurses"),
            ("Respiratory Therapist", "0555", "29-1126", "Respiratory Therapists"),
            ("Social Worker I", "0560", "21-1021", "Child, Family, and School Social Workers"),
            ("Social Worker II", "0561", "21-1021", "Child, Family, and School Social Workers"),
            ("Social Worker III", "0562", "21-1021", "Child, Family, and School Social Workers"),
            ("Speech Pathologist", "0565", "29-1127", "Speech-Language Pathologists"),
            ("Substance Abuse Counselor", "0570", "21-1011", "Substance Abuse and Behavioral Disorder Counselors"),

            # Law Enforcement and Corrections
            ("Capitol Police Officer", "0601", "33-3051", "Police and Sheriff's Patrol Officers"),
            ("Conservation Officer", "0602", "33-3031", "Fish and Game Wardens"),
            ("Correctional Officer I", "0605", "33-3012", "Correctional Officers and Jailers"),
            ("Correctional Officer II", "0606", "33-3012", "Correctional Officers and Jailers"),
            ("Correctional Sergeant", "0607", "33-1011", "First-Line Supervisors of Correctional Officers"),
            ("Criminal Investigator", "0610", "33-3021", "Detectives and Criminal Investigators"),
            ("Deputy Sheriff", "0615", "33-3051", "Police and Sheriff's Patrol Officers"),
            ("Parole Officer", "0620", "21-1092", "Probation Officers and Correctional Treatment Specialists"),
            ("Police Officer I", "0625", "33-3051", "Police and Sheriff's Patrol Officers"),
            ("Police Officer II", "0626", "33-3051", "Police and Sheriff's Patrol Officers"),
            ("Police Sergeant", "0627", "33-1012", "First-Line Supervisors of Police and Detectives"),
            ("Probation Officer I", "0630", "21-1092", "Probation Officers and Correctional Treatment Specialists"),
            ("Probation Officer II", "0631", "21-1092", "Probation Officers and Correctional Treatment Specialists"),
            ("State Trooper", "0635", "33-3051", "Police and Sheriff's Patrol Officers"),
            ("Youth Services Worker", "0640", "21-1093", "Social and Human Service Assistants"),

            # Legal
            ("Assistant Attorney General", "0701", "23-1011", "Lawyers"),
            ("Court Clerk", "0702", "43-4031", "Court, Municipal, and License Clerks"),
            ("Court Reporter", "0703", "23-2091", "Court Reporters"),
            ("Hearing Examiner", "0704", "23-1022", "Arbitrators, Mediators, and Conciliators"),
            ("Judge", "0705", "23-1023", "Judges, Magistrate Judges, and Magistrates"),
            ("Legal Secretary", "0706", "43-6012", "Legal Secretaries"),
            ("Magistrate", "0707", "23-1023", "Judges, Magistrate Judges, and Magistrates"),
            ("Paralegal", "0708", "23-2011", "Paralegals and Legal Assistants"),
            ("Public Defender", "0709", "23-1011", "Lawyers"),
            ("Staff Attorney", "0710", "23-1011", "Lawyers"),

            # Education
            ("Education Specialist", "0801", "25-9099", "Education, Training, and Library Workers, All Other"),
            ("Elementary Teacher", "0802", "25-2021", "Elementary School Teachers"),
            ("High School Teacher", "0803", "25-2031", "High School Teachers"),
            ("Librarian I", "0810", "25-4022", "Librarians"),
            ("Librarian II", "0811", "25-4022", "Librarians"),
            ("Library Technician", "0812", "25-4031", "Library Technicians"),
            ("Principal", "0815", "11-9032", "Education Administrators, K-12"),
            ("School Counselor", "0820", "21-1012", "Educational, Guidance, and Career Counselors"),
            ("School Psychologist", "0821", "19-3031", "Clinical and Counseling Psychologists"),
            ("Special Education Teacher", "0825", "25-2050", "Special Education Teachers"),
            ("Superintendent", "0830", "11-9033", "Education Administrators, Postsecondary"),
            ("Teacher Aide", "0835", "25-9045", "Teaching Assistants"),
            ("Vocational Instructor", "0840", "25-1194", "Career/Technical Education Teachers"),

            # Environmental and Natural Resources
            ("Biologist I", "0901", "19-1020", "Biological Scientists"),
            ("Biologist II", "0902", "19-1020", "Biological Scientists"),
            ("Environmental Analyst", "0905", "19-2041", "Environmental Scientists"),
            ("Environmental Inspector", "0906", "19-4042", "Environmental Science Technicians"),
            ("Environmental Program Manager", "0907", "11-9121", "Natural Sciences Managers"),
            ("Fish and Wildlife Biologist", "0910", "19-1023", "Zoologists and Wildlife Biologists"),
            ("Forester I", "0915", "19-1032", "Foresters"),
            ("Forester II", "0916", "19-1032", "Foresters"),
            ("Geologist", "0920", "19-2042", "Geoscientists"),
            ("Hydrologist", "0921", "19-2043", "Hydrologists"),
            ("Natural Resources Manager", "0925", "11-9121", "Natural Sciences Managers"),
            ("Park Manager", "0930", "11-9121", "Natural Sciences Managers"),
            ("Park Ranger", "0931", "33-3031", "Fish and Game Wardens"),
            ("Water Quality Specialist", "0935", "19-2041", "Environmental Scientists"),

            # Human Resources
            ("Benefits Administrator", "1001", "13-1071", "Human Resources Specialists"),
            ("Classification Analyst", "1002", "13-1071", "Human Resources Specialists"),
            ("Compensation Analyst", "1003", "13-1141", "Compensation, Benefits, and Job Analysis Specialists"),
            ("Employee Relations Specialist", "1004", "13-1071", "Human Resources Specialists"),
            ("HR Director", "1005", "11-3121", "Human Resources Managers"),
            ("HR Generalist", "1006", "13-1071", "Human Resources Specialists"),
            ("HR Manager", "1007", "11-3121", "Human Resources Managers"),
            ("Labor Relations Specialist", "1010", "13-1075", "Labor Relations Specialists"),
            ("Payroll Administrator", "1015", "43-3051", "Payroll and Timekeeping Clerks"),
            ("Personnel Analyst", "1016", "13-1071", "Human Resources Specialists"),
            ("Recruiter", "1020", "13-1071", "Human Resources Specialists"),
            ("Training Coordinator", "1025", "13-1151", "Training and Development Specialists"),
            ("Training Specialist", "1026", "13-1151", "Training and Development Specialists"),

            # Maintenance and Trades
            ("Building Maintenance Worker", "1101", "49-9071", "Maintenance and Repair Workers, General"),
            ("Carpenter", "1102", "47-2031", "Carpenters"),
            ("Custodian", "1103", "37-2011", "Janitors and Cleaners"),
            ("Electrician", "1104", "47-2111", "Electricians"),
            ("Equipment Operator", "1105", "47-2073", "Operating Engineers and Other Construction Equipment Operators"),
            ("Groundskeeper", "1106", "37-3011", "Landscaping and Groundskeeping Workers"),
            ("Heavy Equipment Mechanic", "1107", "49-3042", "Mobile Heavy Equipment Mechanics"),
            ("Highway Maintenance Worker", "1108", "47-4051", "Highway Maintenance Workers"),
            ("HVAC Technician", "1110", "49-9021", "Heating, Air Conditioning, and Refrigeration Mechanics"),
            ("Locksmith", "1115", "49-9094", "Locksmiths and Safe Repairers"),
            ("Maintenance Supervisor", "1116", "49-1011", "First-Line Supervisors of Mechanics"),
            ("Mechanic I", "1120", "49-3023", "Automotive Service Technicians and Mechanics"),
            ("Mechanic II", "1121", "49-3023", "Automotive Service Technicians and Mechanics"),
            ("Painter", "1125", "47-2141", "Painters, Construction and Maintenance"),
            ("Plumber", "1130", "47-2152", "Plumbers, Pipefitters, and Steamfitters"),
            ("Welder", "1135", "51-4121", "Welders, Cutters, Solderers, and Brazers"),

            # Transportation
            ("Bus Driver", "1201", "53-3021", "Bus Drivers, Transit and Intercity"),
            ("CDL Driver", "1202", "53-3032", "Heavy and Tractor-Trailer Truck Drivers"),
            ("Dispatcher", "1203", "43-5032", "Dispatchers"),
            ("Fleet Manager", "1204", "11-3071", "Transportation, Storage, and Distribution Managers"),
            ("School Bus Driver", "1205", "53-3022", "Bus Drivers, School"),
            ("Transportation Manager", "1206", "11-3071", "Transportation, Storage, and Distribution Managers"),
            ("Vehicle Inspector", "1207", "53-6051", "Transportation Inspectors"),

            # Communications and Public Relations
            ("Communications Director", "1301", "11-2031", "Public Relations Managers"),
            ("Graphic Designer", "1302", "27-1024", "Graphic Designers"),
            ("Media Relations Specialist", "1303", "27-3031", "Public Relations Specialists"),
            ("Public Information Officer", "1304", "27-3031", "Public Relations Specialists"),
            ("Social Media Coordinator", "1305", "27-3031", "Public Relations Specialists"),
            ("Web Content Manager", "1306", "15-1254", "Web Developers"),
            ("Writer/Editor", "1307", "27-3041", "Editors"),

            # Emergency Services
            ("911 Dispatcher", "1401", "43-5031", "Public Safety Telecommunicators"),
            ("Emergency Management Coordinator", "1402", "11-9161", "Emergency Management Directors"),
            ("Emergency Management Director", "1403", "11-9161", "Emergency Management Directors"),
            ("Fire Chief", "1404", "33-1021", "First-Line Supervisors of Firefighting"),
            ("Fire Inspector", "1405", "33-2021", "Fire Inspectors and Investigators"),
            ("Firefighter", "1406", "33-2011", "Firefighters"),
            ("Paramedic", "1407", "29-2043", "Paramedics"),

            # Social Services
            ("Case Manager", "1501", "21-1021", "Child, Family, and School Social Workers"),
            ("Child Protective Services Worker", "1502", "21-1021", "Child, Family, and School Social Workers"),
            ("Community Health Worker", "1503", "21-1094", "Community Health Workers"),
            ("Economic Services Worker", "1504", "43-4061", "Eligibility Interviewers, Government Programs"),
            ("Eligibility Specialist", "1505", "43-4061", "Eligibility Interviewers, Government Programs"),
            ("Family Services Specialist", "1506", "21-1021", "Child, Family, and School Social Workers"),
            ("Food Stamp Worker", "1507", "43-4061", "Eligibility Interviewers, Government Programs"),
            ("Program Administrator", "1510", "11-9151", "Social and Community Service Managers"),
            ("Social Services Director", "1511", "11-9151", "Social and Community Service Managers"),
            ("Vocational Rehabilitation Counselor", "1515", "21-1015", "Rehabilitation Counselors"),

            # Procurement and Supply
            ("Buyer", "1601", "13-1023", "Purchasing Agents"),
            ("Contract Administrator", "1602", "13-1023", "Purchasing Agents"),
            ("Inventory Control Specialist", "1603", "43-5081", "Stock Clerks and Order Fillers"),
            ("Procurement Officer", "1604", "11-3061", "Purchasing Managers"),
            ("Purchasing Agent", "1605", "13-1023", "Purchasing Agents"),
            ("Warehouse Manager", "1606", "11-3071", "Transportation, Storage, and Distribution Managers"),
            ("Warehouse Worker", "1607", "53-7062", "Laborers and Freight, Stock, and Material Movers"),

            # Regulatory and Inspection
            ("Agricultural Inspector", "1701", "45-2011", "Agricultural Inspectors"),
            ("Building Inspector", "1702", "47-4011", "Construction and Building Inspectors"),
            ("Compliance Officer", "1703", "13-1041", "Compliance Officers"),
            ("Electrical Inspector", "1704", "47-4011", "Construction and Building Inspectors"),
            ("Food Inspector", "1705", "45-2011", "Agricultural Inspectors"),
            ("Health Inspector", "1706", "29-9011", "Occupational Health and Safety Specialists"),
            ("License Examiner", "1707", "43-4031", "Court, Municipal, and License Clerks"),
            ("Occupational Safety Inspector", "1708", "29-9011", "Occupational Health and Safety Specialists"),
            ("Plumbing Inspector", "1709", "47-4011", "Construction and Building Inspectors"),
            ("Regulatory Analyst", "1710", "13-1041", "Compliance Officers"),
            ("Tax Compliance Officer", "1711", "13-1041", "Compliance Officers"),

            # Clerical and Administrative Support
            ("Administrative Aide", "1801", "43-6014", "Secretaries and Administrative Assistants"),
            ("Clerk I", "1802", "43-9061", "Office Clerks, General"),
            ("Clerk II", "1803", "43-9061", "Office Clerks, General"),
            ("Clerk III", "1804", "43-9061", "Office Clerks, General"),
            ("Customer Service Representative", "1805", "43-4051", "Customer Service Representatives"),
            ("Data Entry Clerk", "1806", "43-9021", "Data Entry Keyers"),
            ("File Clerk", "1807", "43-4071", "File Clerks"),
            ("Mail Clerk", "1808", "43-9051", "Mail Clerks and Mail Machine Operators"),
            ("Office Manager", "1809", "43-1011", "First-Line Supervisors of Office Workers"),
            ("Receptionist", "1810", "43-4171", "Receptionists and Information Clerks"),
            ("Records Manager", "1811", "43-4071", "File Clerks"),
            ("Secretary I", "1812", "43-6014", "Secretaries and Administrative Assistants"),
            ("Secretary II", "1813", "43-6014", "Secretaries and Administrative Assistants"),
            ("Switchboard Operator", "1814", "43-2011", "Switchboard Operators"),
            ("Word Processor", "1815", "43-9022", "Word Processors and Typists"),
        ]

        classifications = []
        for title, code, soc_code, soc_title in sample_data:
            # Build classification in standardized format
            classifications.append(JobClassification(
                JobCode=code,
                JobTitleAbbreviation=self._generate_abbreviation(title),
                JobTitleFull=title,
                OccupationalGroupText=soc_title,
                EEOText=self._get_eeo_category(soc_code),
                WorkFunction=self._get_work_function(soc_code, soc_title),
                WorkLevel=self._get_work_level(title),
                SupervisionReceived=self._get_supervision_received(title),
            ))

        self.classifications = classifications
        logger.info(f"Loaded {len(classifications)} sample job classifications")
        return classifications

    def export_to_csv(self, filename: str = "job_classifications.csv") -> str:
        """Export classifications to CSV file"""
        if not self.classifications:
            logger.warning("No classifications to export")
            return ""

        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", filename)

        df = pd.DataFrame([asdict(c) for c in self.classifications])
        df.to_csv(filepath, index=False, quoting=csv.QUOTE_ALL)

        logger.info(f"Exported {len(self.classifications)} classifications to {filepath}")
        return filepath

    def export_to_json(self, filename: str = "job_classifications.json") -> str:
        """Export classifications to JSON file"""
        if not self.classifications:
            logger.warning("No classifications to export")
            return ""

        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([asdict(c) for c in self.classifications], f, indent=2)

        logger.info(f"Exported {len(self.classifications)} classifications to {filepath}")
        return filepath

    def get_summary(self) -> Dict:
        """Get summary statistics of scraped data"""
        if not self.classifications:
            return {"error": "No classifications loaded"}

        occ_groups = [c.OccupationalGroupText for c in self.classifications if c.OccupationalGroupText]
        unique_occ = set(occ_groups)
        eeo_categories = set(c.EEOText for c in self.classifications if c.EEOText)

        return {
            "total_classifications": len(self.classifications),
            "unique_occupational_groups": len(unique_occ),
            "eeo_categories": len(eeo_categories),
            "coverage": f"{len(occ_groups)/len(self.classifications)*100:.1f}%",
        }


def main():
    """Main function to run the job classification scraper"""
    import argparse

    parser = argparse.ArgumentParser(description="Job Classification Web Scraper")
    parser.add_argument('--state', default='wv', help='State abbreviation (default: wv)')
    parser.add_argument('--output', default='job_classifications.csv', help='Output filename')
    parser.add_argument('--sample', action='store_true', help='Use sample data')
    parser.add_argument('--format', choices=['csv', 'json', 'both'], default='csv', help='Output format')

    args = parser.parse_args()

    scraper = JobClassificationScraper()

    print("\n" + "=" * 60)
    print("JOB CLASSIFICATION SCRAPER")
    print("=" * 60)

    if args.sample:
        print(f"\nLoading sample data for West Virginia...")
        classifications = scraper.load_from_sample_data()
    else:
        print(f"\nScraping job classifications for state: {args.state.upper()}")
        classifications = scraper.scrape_governmentjobs(args.state)

    if not classifications:
        print("No classifications found!")
        return

    # Export data
    if args.format in ['csv', 'both']:
        csv_file = scraper.export_to_csv(args.output)
        print(f"\n✅ CSV exported to: {csv_file}")

    if args.format in ['json', 'both']:
        json_file = scraper.export_to_json(args.output.replace('.csv', '.json'))
        print(f"✅ JSON exported to: {json_file}")

    # Print summary
    summary = scraper.get_summary()
    print(f"\n📊 SUMMARY:")
    print(f"   Total Classifications: {summary['total_classifications']}")
    print(f"   Unique Occupational Groups: {summary['unique_occupational_groups']}")
    print(f"   EEO Categories: {summary['eeo_categories']}")
    print(f"   Coverage: {summary['coverage']}")

    # Print sample in standardized format
    print(f"\n📋 SAMPLE OUTPUT (first 10 records):")
    print("-" * 120)
    print(f"{'JobCode':<8} {'JobTitleAbbrev':<20} {'JobTitleFull':<30} {'OccupationalGroupText':<35} {'EEOText':<25}")
    print("-" * 120)
    for c in classifications[:10]:
        print(f"{c.JobCode:<8} {c.JobTitleAbbreviation[:19]:<20} {c.JobTitleFull[:29]:<30} {c.OccupationalGroupText[:34]:<35} {c.EEOText[:24]:<25}")

    print("\n📋 WORK DETAILS (first 5 records):")
    print("-" * 120)
    print(f"{'JobCode':<8} {'WorkLevel':<15} {'SupervisionReceived':<50} {'WorkFunction':<45}")
    print("-" * 120)
    for c in classifications[:5]:
        print(f"{c.JobCode:<8} {c.WorkLevel[:14]:<15} {c.SupervisionReceived[:49]:<50} {c.WorkFunction[:44]:<45}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

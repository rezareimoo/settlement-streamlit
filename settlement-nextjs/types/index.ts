// Database Types
export interface SettlementCase {
  caseid: string;
  region: string;
  jamatkhana: string;
  status: string;
  creationdate: Date | string;
  openreopendate: Date | string | null;
  lastlogdate: Date | string | null;
  firstname: string;
  lastname: string;
  phonenumber: string;
  email: string;
  city: string;
  state: string;
  zip: string;
  assignedto: string;
  numfamilyemployed: number | null;
  inputtype: string | null;
}

export interface JamatiMember {
  personid: number;
  caseid: string;
  firstname: string;
  lastname: string;
  yearofbirth: number;
  countryoforigin: string;
  relationtohead: string;
  legalstatus: string;
  usarrivalyear: number;
  borninusa: boolean;
  englishfluency: string;
  educationlevel: string;
}

export interface Education {
  educationid: number;
  personid: number;
  englishfluency: string;
  educationlevel: string;
  isattendingecdc: boolean;
  isattendingrec: boolean;
  isattendingschool: boolean;
  schoolname: string | null;
  schoolgrade: string | null;
  attendancetype: string | null;
  hasextracurriculars: boolean;
  hasacademicissues: boolean;
  academicperformance: string | null;
  academicassistancetype: string | null;
  comfortablewithteacher: boolean;
  comfortablewithteachercomments: string | null;
  isbullied: boolean;
  hasbehaviorchallenges: boolean;
  hasdisability: boolean;
  hasspecializedlearningplans: boolean;
  iscoping: boolean;
  hasotherchallenges: boolean;
  hasotherchallengescomments: string | null;
  shareinfowitheboryeb: boolean;
  educationcomments: string | null;
}

export interface SocialInclusionAgency {
  socialinclusionid: number;
  personid: number;
  socialinclusiondomainstatus: string;
  socialinclusiondomaingoalstatus: string | null;
  commutingtype: string | null;
  hascommunityconnection: boolean;
  jkinstitutionalacceptance: boolean;
  socialsupportcomments: string | null;
  hasfriendfamilyconnection: boolean;
  familyfriendconnectioncomments: string | null;
  familyrelationshipcomments: string | null;
  attendjk: boolean;
  attendjkhowoften: string | null;
  reasonfornotattendingjk: string | null;
  assistancesocialintegration: boolean;
  hascellphoneaccess: boolean;
  cellphoneaccesscomments: string | null;
  currentsituation: string | null;
  currentsituationcomments: string | null;
}

export interface Finance {
  financeid: number;
  personid: number;
  financedomainstatus: string;
  financedomaingoalstatus: string | null;
  hasgovernmentbenefits: boolean;
  governmentbenefits: string | null;
  nogovernmentbenefitscomments: string | null;
  taxfiling: boolean;
  assettype: string | null;
  assetscomments: string | null;
  havedebt: boolean;
  debtcomments: string | null;
  sendmoneybackhome: boolean;
  financialsupport: boolean;
  financialsupportcomments: string | null;
  ishelpneededmanagingfinance: boolean;
  helpmanagingfinancecomments: string | null;
  sharecontactinfoforfinplanning: boolean;
  sharecontactinfoforfinplanningcomments: string | null;
}

export interface PhysicalMentalHealth {
  healthid: number;
  personid: number;
  healthdomainstatus: string;
  healthdomaingoalstatus: string | null;
  hasmedicalconditions: boolean;
  medicalcomments: string | null;
  iscostpreventingmedicalcare: boolean;
  costpreventingmedicalcarecomments: string | null;
  havehealthinsurance: boolean;
  typeofhealthinsurance: string | null;
  healthinsurancecomments: string | null;
  hasprimarycaredoctor: boolean;
  primarycaredoctorcomments: string | null;
  preventivecareexams: boolean;
  preventivecareexamscomments: string | null;
  shareinfowithakhb: boolean;
  shareinfowithakhbcomments: string | null;
  hasphysicaldisability: boolean;
  physicaldisabilitycomments: string | null;
  littleinterestorpleasurefrequency: string | null;
  littleinterestcomments: string | null;
  depressionfrequency: string | null;
  depressioncomments: string | null;
  anxiousfrequency: string | null;
  anxiouscomments: string | null;
  worryfrequency: string | null;
  worrycomments: string | null;
  relationshipfrequency: string | null;
  familyrelationshipcomments: string | null;
  substanceuseaffectswork: boolean;
  substanceusecomments: string | null;
  hasstressmanagementstrategies: boolean;
  stressmanagementcomments: string | null;
}

export interface FDPCase {
  access_case: string;
  settlement_case_status: string;
  family_last_name: string;
  head_of_family_first_name: string;
  state_code_2_digits: string;
  access_case_creation_date: Date | string;
  settlement_cm: string;
  phone: string;
  current_location: string;
  zip_code: string;
  region: string;
  number_in_family: number;
}

export interface CustomData {
  case_id: string;
  family_progress_status: string;
  languages_spoken: string[];
  arrival_date: Date | string;
}

// API Response Types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

// Filter Types
export interface DateFilter {
  startDate: Date | null;
  endDate: Date | null;
}

export interface CaseFilters extends DateFilter {
  region: string;
  dataSource: 'CMS' | 'FDP' | 'COMPARE';
}

CREATE TABLE SettlementCase (
    CaseID VARCHAR (20) PRIMARY KEY,
    Region VARCHAR(2),
    JamatKhana VARCHAR(50),
    Status VARCHAR(10),
    CreationDate DATE,
    OpenReopenDate DATE,
    LastLogDate DATE,
	FirstName VARCHAR(50),
	LastName VARCHAR(50),
	PhoneNumber VARCHAR(15),
	Email VARCHAR(100),
	CITY VARCHAR(50),
	STATE VARCHAR(2),
	ZIP VARCHAR(5),
    AssignedTo VARCHAR(100),
	NumFamilyEmployed INT,
    inputtype VARCHAR(50)
);

CREATE TABLE JamatiMember (
    PersonID SERIAL PRIMARY KEY,
    CaseID VARCHAR(20) REFERENCES SettlementCase(CaseID) ON DELETE CASCADE,
    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    YearOfBirth INT,
    CountryOfOrigin VARCHAR(100),
    RelationToHead VARCHAR(50),
    LegalStatus VARCHAR(50),
    USArrivalYear INT,
    BornInUSA BOOLEAN,
    EnglishFluency VARCHAR(50),
    EducationLevel VARCHAR(100)
);


-- Education Table
CREATE TABLE Education (
    EducationID SERIAL PRIMARY KEY,
    PersonID INT REFERENCES JamatiMember(PersonID),
    EnglishFluency VARCHAR(50),
    EducationLevel VARCHAR(50),
    IsAttendingECDC BOOLEAN,
    IsAttendingREC BOOLEAN,
    IsAttendingSchool BOOLEAN,
    SchoolName VARCHAR(100),
    SchoolGrade VARCHAR(50),
    AttendanceType VARCHAR(50),
    HasExtraCurriculars BOOLEAN,
    HasAcademicIssues BOOLEAN,
    AcademicPerformance VARCHAR(50),
    AcademicAssistanceType VARCHAR(100),
    ComfortableWithTeacher BOOLEAN,
    ComfortableWithTeacherComments TEXT,
    IsBullied BOOLEAN,
    HasBehaviorChallenges BOOLEAN,
    HasDisability BOOLEAN,
    HasSpecializedLearningPlans BOOLEAN,
    IsCoping BOOLEAN,
    HasOtherChallenges BOOLEAN,
    HasOtherChallengesComments TEXT,
    ShareInfoWithEBorYSB BOOLEAN,
    EducationComments TEXT
);

-- Social Inclusion and Agency Table
CREATE TABLE SocialInclusionAgency (
    SocialInclusionID SERIAL PRIMARY KEY,
    PersonID INT REFERENCES JamatiMember(PersonID),
    SocialInclusionDomainStatus VARCHAR(50),
    SocialInclusionDomainGoalStatus VARCHAR(50),
    CommutingType VARCHAR(50),
    HasCommunityConnection BOOLEAN,
    JkInstitutionalAcceptance BOOLEAN,
    SocialSupportComments TEXT,
    HasFriendFamilyConnection BOOLEAN,
    FamilyFriendConnectionComments TEXT,
    FamilyRelationshipComments TEXT,
    AttendJK BOOLEAN,
    AttendJkHowOften VARCHAR(50),
    ReasonForNotAttendingJK TEXT,
    AssistanceSocialIntegration BOOLEAN,
    HasCellPhoneAccess BOOLEAN,
    CellPhoneAccessComments TEXT,
    CurrentSituation VARCHAR(50),
    CurrentSituationComments TEXT
);

-- Finance Table
CREATE TABLE Finance (
    FinanceID SERIAL PRIMARY KEY,
    PersonID INT REFERENCES JamatiMember(PersonID),
    FinanceDomainStatus VARCHAR(50),
    FinanceDomainGoalStatus VARCHAR(50),
    HasGovernmentBenefits BOOLEAN,
    GovernmentBenefits TEXT,
    NoGovernmentBenefitsComments TEXT,
    TaxFiling BOOLEAN,
    AssetType TEXT,
    AssetsComments TEXT,
    HaveDebt BOOLEAN,
    DebtComments TEXT,
    SendMoneyBackHome BOOLEAN,
    FinancialSupport BOOLEAN,
    FinancialSupportComments TEXT,
    IsHelpNeededManagingFinance BOOLEAN,
    HelpManagingFinanceComments TEXT,
    ShareContactInfoForFinPlanning BOOLEAN,
    ShareContactInfoForFinPlanningComments TEXT
);

-- Physical and Mental Health Table
CREATE TABLE PhysicalMentalHealth (
    HealthID SERIAL PRIMARY KEY,
    PersonID INT REFERENCES JamatiMember(PersonID),
    HealthDomainStatus VARCHAR(50),
    HealthDomainGoalStatus VARCHAR(50),
    HasMedicalConditions BOOLEAN,
    MedicalComments TEXT,
    IsCostPreventingMedicalCare BOOLEAN,
    CostPreventingMedicalCareComments TEXT,
    HaveHealthInsurance BOOLEAN,
    TypeOfHealthInsurance VARCHAR(50),
    HealthInsuranceComments TEXT,
    HasPrimaryCareDoctor BOOLEAN,
    PrimaryCareDoctorComments TEXT,
    PreventiveCareExams BOOLEAN,
    PreventiveCareExamsComments TEXT,
    ShareInfoWithAKHB BOOLEAN,
    ShareInfoWithAKHBComments TEXT,
    HasPhysicalDisability BOOLEAN,
    PhysicalDisabilityComments TEXT,
    LittleInterestOrPleasureFrequency VARCHAR(50),
    LittleInterestComments TEXT,
    DepressionFrequency VARCHAR(50),
    DepressionComments TEXT,
    AnxiousFrequency VARCHAR(50),
    AnxiousComments TEXT,
    WorryFrequency VARCHAR(50),
    WorryComments TEXT,
    RelationshipFrequency VARCHAR(50),
    FamilyRelationshipComments TEXT,
    SubstanceUseAffectsWork BOOLEAN,
    SubstanceUseComments TEXT,
    HasStreeManagementStrategies BOOLEAN,
    StressManagementComments TEXT
);

CREATE TABLE user_accounts (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    regions TEXT[],
    password VARCHAR(20) NOT NULL
);
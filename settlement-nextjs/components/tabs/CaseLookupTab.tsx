"use client";

import { useState, useEffect } from "react";
import {
  SettlementCase,
  JamatiMember,
  Education,
  Finance,
  PhysicalMentalHealth,
  SocialInclusionAgency,
  CustomData,
} from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ChevronDown, ChevronUp } from "lucide-react";
import { formatDate } from "@/lib/utils";

export function CaseLookupTab() {
  const [cases, setCases] = useState<SettlementCase[]>([]);
  const [members, setMembers] = useState<JamatiMember[]>([]);
  const [education, setEducation] = useState<Education[]>([]);
  const [finance, setFinance] = useState<Finance[]>([]);
  const [health, setHealth] = useState<PhysicalMentalHealth[]>([]);
  const [socialInclusion, setSocialInclusion] = useState<
    SocialInclusionAgency[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [selectedCaseId, setSelectedCaseId] = useState<string>("");
  const [customData, setCustomData] = useState<CustomData | null>(null);
  const [showAssessmentForm, setShowAssessmentForm] = useState(false);
  const [caseInfoOpen, setCaseInfoOpen] = useState(true);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const [casesRes, membersRes, educationRes, financeRes, healthRes, socialRes] =
          await Promise.all([
            fetch("/api/cases"),
            fetch("/api/members"),
            fetch("/api/education"),
            fetch("/api/finance"),
            fetch("/api/health"),
            fetch("/api/social-inclusion"),
          ]);

        const casesData = await casesRes.json();
        const membersData = await membersRes.json();
        const educationData = await educationRes.json();
        const financeData = await financeRes.json();
        const healthData = await healthRes.json();
        const socialData = await socialRes.json();

        setCases(casesData.data || []);
        setMembers(membersData.data || []);
        setEducation(educationData.data || []);
        setFinance(financeData.data || []);
        setHealth(healthData.data || []);
        setSocialInclusion(socialData.data || []);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  useEffect(() => {
    if (selectedCaseId) {
      fetchCustomData(selectedCaseId);
    }
  }, [selectedCaseId]);

  async function fetchCustomData(caseId: string) {
    try {
      const res = await fetch(`/api/custom-data/${caseId}`);
      const data = await res.json();
      setCustomData(data.data);
    } catch (error) {
      console.error("Error fetching custom data:", error);
      setCustomData(null);
    }
  }

  if (loading) {
    return <div className="p-4">Loading case data...</div>;
  }

  const selectedCase = cases.find((c) => c.caseid === selectedCaseId);
  const caseMembers = members.filter((m) => m.caseid === selectedCaseId);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Settlement Case Lookup</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label className="font-medium">Select or type a Case ID:</label>
              <Select value={selectedCaseId} onValueChange={setSelectedCaseId}>
                <SelectTrigger className="w-full mt-2">
                  <SelectValue placeholder="Select a case" />
                </SelectTrigger>
                <SelectContent>
                  {cases.map((c) => (
                    <SelectItem key={c.caseid} value={c.caseid}>
                      {c.caseid} - {c.firstname} {c.lastname}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {selectedCase && (
        <>
          {/* Case Information */}
          <Collapsible open={caseInfoOpen} onOpenChange={setCaseInfoOpen}>
            <Card>
              <CardHeader>
                <CollapsibleTrigger className="flex items-center justify-between w-full">
                  <CardTitle>Case Information</CardTitle>
                  {caseInfoOpen ? <ChevronUp /> : <ChevronDown />}
                </CollapsibleTrigger>
              </CardHeader>
              <CollapsibleContent>
                <CardContent>
                  <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <h3 className="font-semibold text-lg">Basic Information</h3>
                      <div className="space-y-1 text-sm">
                        <p><strong>Case ID:</strong> {selectedCase.caseid}</p>
                        <p><strong>Region:</strong> {selectedCase.region}</p>
                        <p><strong>Jamat Khana:</strong> {selectedCase.jamatkhana}</p>
                        <p><strong>Status:</strong> {selectedCase.status}</p>
                        <p><strong>Assigned To:</strong> {selectedCase.assignedto}</p>
                        <p>
                          <strong>Input Type:</strong>{" "}
                          {selectedCase.inputtype || "N/A"}
                        </p>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <h3 className="font-semibold text-lg">Contact Information</h3>
                      <div className="space-y-1 text-sm">
                        <p>
                          <strong>Name:</strong> {selectedCase.firstname}{" "}
                          {selectedCase.lastname}
                        </p>
                        <p><strong>Phone:</strong> {selectedCase.phonenumber}</p>
                        <p><strong>Email:</strong> {selectedCase.email}</p>
                        <p>
                          <strong>Location:</strong> {selectedCase.city},{" "}
                          {selectedCase.state} {selectedCase.zip}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 space-y-1 text-sm">
                    <h3 className="font-semibold text-lg">Case Timeline</h3>
                    <p>
                      <strong>Creation Date:</strong>{" "}
                      {formatDate(selectedCase.creationdate)}
                    </p>
                    <p>
                      <strong>Open/Reopen Date:</strong>{" "}
                      {formatDate(selectedCase.openreopendate)}
                    </p>
                    <p>
                      <strong>Last Log Date:</strong>{" "}
                      {formatDate(selectedCase.lastlogdate)}
                    </p>
                  </div>
                </CardContent>
              </CollapsibleContent>
            </Card>
          </Collapsible>

          {/* Custom Data Display */}
          {customData && (
            <Card>
              <CardHeader>
                <CardTitle>Quick Assessment Data</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p>
                      <strong>Family Progress Status:</strong>{" "}
                      {customData.family_progress_status}
                    </p>
                    <p>
                      <strong>Arrival Date:</strong>{" "}
                      {formatDate(customData.arrival_date)}
                    </p>
                  </div>
                  <div>
                    <p>
                      <strong>Languages Spoken:</strong>{" "}
                      {Array.isArray(customData.languages_spoken)
                        ? customData.languages_spoken.join(", ")
                        : "None specified"}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Quick Assessment Button */}
          <div>
            <Button onClick={() => setShowAssessmentForm(!showAssessmentForm)}>
              {customData ? "Edit Quick Assessment" : "Add Quick Assessment"}
            </Button>
          </div>

          {/* Family Members */}
          <div className="space-y-4">
            <h2 className="text-2xl font-bold">
              Family Members ({caseMembers.length})
            </h2>
            {caseMembers.map((member) => {
              const memberEducation = education.find(
                (e) => e.personid === member.personid
              );
              const memberFinance = finance.find(
                (f) => f.personid === member.personid
              );
              const memberHealth = health.find(
                (h) => h.personid === member.personid
              );
              const memberSocial = socialInclusion.find(
                (s) => s.personid === member.personid
              );

              return (
                <Collapsible key={member.personid}>
                  <Card>
                    <CardHeader>
                      <CollapsibleTrigger className="flex items-center justify-between w-full">
                        <CardTitle>
                          {member.firstname} {member.lastname} (
                          {member.relationtohead})
                        </CardTitle>
                        <ChevronDown />
                      </CollapsibleTrigger>
                    </CardHeader>
                    <CollapsibleContent>
                      <CardContent>
                        <Tabs defaultValue="personal">
                          <TabsList className="grid w-full grid-cols-5">
                            <TabsTrigger value="personal">Personal Info</TabsTrigger>
                            <TabsTrigger value="education">Education</TabsTrigger>
                            <TabsTrigger value="social">Social Inclusion</TabsTrigger>
                            <TabsTrigger value="finance">Finance</TabsTrigger>
                            <TabsTrigger value="health">Health</TabsTrigger>
                          </TabsList>
                          <TabsContent value="personal" className="space-y-2 mt-4 text-sm">
                            <p>
                              <strong>Name:</strong> {member.firstname}{" "}
                              {member.lastname}
                            </p>
                            <p>
                              <strong>Relation to Head:</strong>{" "}
                              {member.relationtohead}
                            </p>
                            <p>
                              <strong>Year of Birth:</strong> {member.yearofbirth}
                            </p>
                            <p>
                              <strong>Age:</strong>{" "}
                              {new Date().getFullYear() - member.yearofbirth}
                            </p>
                            <p>
                              <strong>Country of Origin:</strong>{" "}
                              {member.countryoforigin}
                            </p>
                            <p>
                              <strong>Legal Status:</strong> {member.legalstatus}
                            </p>
                            <p>
                              <strong>USA Arrival Year:</strong>{" "}
                              {member.usarrivalyear}
                            </p>
                            <p>
                              <strong>Born in USA:</strong>{" "}
                              {member.borninusa ? "Yes" : "No"}
                            </p>
                            <p>
                              <strong>English Fluency:</strong>{" "}
                              {member.englishfluency}
                            </p>
                            <p>
                              <strong>Education Level:</strong>{" "}
                              {member.educationlevel}
                            </p>
                          </TabsContent>
                          <TabsContent value="education" className="mt-4 text-sm">
                            {memberEducation ? (
                              <div className="space-y-2">
                                <p>
                                  <strong>Attending School:</strong>{" "}
                                  {memberEducation.isattendingschool ? "Yes" : "No"}
                                </p>
                                {memberEducation.isattendingschool && (
                                  <>
                                    <p>
                                      <strong>School Name:</strong>{" "}
                                      {memberEducation.schoolname || "N/A"}
                                    </p>
                                    <p>
                                      <strong>Grade:</strong>{" "}
                                      {memberEducation.schoolgrade || "N/A"}
                                    </p>
                                  </>
                                )}
                                <p>
                                  <strong>Academic Performance:</strong>{" "}
                                  {memberEducation.academicperformance || "N/A"}
                                </p>
                                <p>
                                  <strong>Has Academic Issues:</strong>{" "}
                                  {memberEducation.hasacademicissues ? "Yes" : "No"}
                                </p>
                              </div>
                            ) : (
                              <p className="text-muted-foreground">
                                No education data available
                              </p>
                            )}
                          </TabsContent>
                          <TabsContent value="social" className="mt-4 text-sm">
                            {memberSocial ? (
                              <div className="space-y-2">
                                <p>
                                  <strong>Domain Status:</strong>{" "}
                                  {memberSocial.socialinclusiondomainstatus}
                                </p>
                                <p>
                                  <strong>Community Connection:</strong>{" "}
                                  {memberSocial.hascommunityconnection ? "Yes" : "No"}
                                </p>
                                <p>
                                  <strong>Attends JK:</strong>{" "}
                                  {memberSocial.attendjk ? "Yes" : "No"}
                                </p>
                                {memberSocial.attendjk && (
                                  <p>
                                    <strong>JK Attendance Frequency:</strong>{" "}
                                    {memberSocial.attendjkhowoften || "N/A"}
                                  </p>
                                )}
                              </div>
                            ) : (
                              <p className="text-muted-foreground">
                                No social inclusion data available
                              </p>
                            )}
                          </TabsContent>
                          <TabsContent value="finance" className="mt-4 text-sm">
                            {memberFinance ? (
                              <div className="space-y-2">
                                <p>
                                  <strong>Domain Status:</strong>{" "}
                                  {memberFinance.financedomainstatus}
                                </p>
                                <p>
                                  <strong>Government Benefits:</strong>{" "}
                                  {memberFinance.hasgovernmentbenefits ? "Yes" : "No"}
                                </p>
                                <p>
                                  <strong>Tax Filing:</strong>{" "}
                                  {memberFinance.taxfiling ? "Yes" : "No"}
                                </p>
                                <p>
                                  <strong>Has Debt:</strong>{" "}
                                  {memberFinance.havedebt ? "Yes" : "No"}
                                </p>
                              </div>
                            ) : (
                              <p className="text-muted-foreground">
                                No finance data available
                              </p>
                            )}
                          </TabsContent>
                          <TabsContent value="health" className="mt-4 text-sm">
                            {memberHealth ? (
                              <div className="space-y-2">
                                <p>
                                  <strong>Domain Status:</strong>{" "}
                                  {memberHealth.healthdomainstatus}
                                </p>
                                <p>
                                  <strong>Medical Conditions:</strong>{" "}
                                  {memberHealth.hasmedicalconditions ? "Yes" : "No"}
                                </p>
                                <p>
                                  <strong>Health Insurance:</strong>{" "}
                                  {memberHealth.havehealthinsurance ? "Yes" : "No"}
                                </p>
                                {memberHealth.havehealthinsurance && (
                                  <p>
                                    <strong>Insurance Type:</strong>{" "}
                                    {memberHealth.typeofhealthinsurance || "N/A"}
                                  </p>
                                )}
                                <p>
                                  <strong>Primary Care Doctor:</strong>{" "}
                                  {memberHealth.hasprimarycaredoctor ? "Yes" : "No"}
                                </p>
                              </div>
                            ) : (
                              <p className="text-muted-foreground">
                                No health data available
                              </p>
                            )}
                          </TabsContent>
                        </Tabs>
                      </CardContent>
                    </CollapsibleContent>
                  </Card>
                </Collapsible>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

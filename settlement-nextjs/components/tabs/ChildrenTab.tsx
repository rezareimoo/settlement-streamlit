"use client";

import { useState, useEffect } from "react";
import { SettlementCase, JamatiMember, Education } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function ChildrenTab() {
  const [cases, setCases] = useState<SettlementCase[]>([]);
  const [members, setMembers] = useState<JamatiMember[]>([]);
  const [education, setEducation] = useState<Education[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const [casesRes, membersRes, educationRes] = await Promise.all([
          fetch("/api/cases"),
          fetch("/api/members"),
          fetch("/api/education"),
        ]);

        const casesData = await casesRes.json();
        const membersData = await membersRes.json();
        const educationData = await educationRes.json();

        setCases(casesData.data || []);
        setMembers(membersData.data || []);
        setEducation(educationData.data || []);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return <div className="p-4">Loading children data...</div>;
  }

  const currentYear = new Date().getFullYear();
  const children = members.filter(
    (m) =>
      m.yearofbirth &&
      m.yearofbirth >= currentYear - 18 &&
      m.yearofbirth <= currentYear
  );

  // Calculate regional summary
  const regions = Array.from(new Set(cases.map((c) => c.region)));
  const regionalSummary = regions.map((region) => {
    const regionCases = cases.filter((c) => c.region === region);
    const regionCaseIds = regionCases.map((c) => c.caseid);
    const regionChildren = children.filter((c) => regionCaseIds.includes(c.caseid));

    const activeCaseIds = cases
      .filter((c) => c.region === region && (c.status === "Open" || c.status === "Reopen"))
      .map((c) => c.caseid);
    const activeChildren = regionChildren.filter((c) =>
      activeCaseIds.includes(c.caseid)
    );

    return {
      region,
      total: regionChildren.length,
      active: activeChildren.length,
    };
  });

  // Age distribution
  const ageDistribution: Record<number, number> = {};
  children.forEach((child) => {
    const age = currentYear - child.yearofbirth;
    ageDistribution[age] = (ageDistribution[age] || 0) + 1;
  });

  // Country distribution
  const countryDistribution: Record<string, number> = {};
  children.forEach((child) => {
    countryDistribution[child.countryoforigin] =
      (countryDistribution[child.countryoforigin] || 0) + 1;
  });

  // Education statistics
  const childrenEducation = education.filter((e) =>
    children.some((c) => c.personid === e.personid)
  );

  const educationStats = {
    attendingSchool: childrenEducation.filter((e) => e.isattendingschool).length,
    attendingECDC: childrenEducation.filter((e) => e.isattendingecdc).length,
    attendingREC: childrenEducation.filter((e) => e.isattendingrec).length,
    hasAcademicIssues: childrenEducation.filter((e) => e.hasacademicissues).length,
    hasExtraCurriculars: childrenEducation.filter((e) => e.hasextracurriculars)
      .length,
    isBullied: childrenEducation.filter((e) => e.isbullied).length,
    hasBehaviorChallenges: childrenEducation.filter((e) => e.hasbehaviorchallenges)
      .length,
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Children's Data (18 and Under)</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Analysis of children in settlement cases, including demographics and
            education statistics.
          </p>
        </CardContent>
      </Card>

      {/* Regional Summary */}
      <Card>
        <CardHeader>
          <CardTitle>📊 Children Summary by Region</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Region</th>
                  <th className="text-left p-2">Total Children</th>
                  <th className="text-left p-2">Children in Active Cases</th>
                </tr>
              </thead>
              <tbody>
                {regionalSummary.map((row) => (
                  <tr key={row.region} className="border-b">
                    <td className="p-2">{row.region}</td>
                    <td className="p-2">{row.total.toLocaleString()}</td>
                    <td className="p-2">{row.active.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Age Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>📈 Children Age Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {Object.entries(ageDistribution)
                .sort(([a], [b]) => parseInt(a) - parseInt(b))
                .map(([age, count]) => (
                  <div key={age} className="flex justify-between items-center text-sm">
                    <span>{age} years old</span>
                    <span className="font-medium">{count}</span>
                  </div>
                ))}
            </div>
            <p className="text-xs text-muted-foreground mt-4">
              Chart visualization will be added with Recharts
            </p>
          </CardContent>
        </Card>

        {/* Country Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>🌍 Children Country of Origin Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {Object.entries(countryDistribution)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 10)
                .map(([country, count]) => (
                  <div key={country} className="flex justify-between items-center text-sm">
                    <span>{country}</span>
                    <span className="font-medium">{count}</span>
                  </div>
                ))}
            </div>
            <p className="text-xs text-muted-foreground mt-4">
              Chart visualization will be added with Recharts
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Education Statistics */}
      <Card>
        <CardHeader>
          <CardTitle>📚 Children's Education Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm">Attending School</span>
                <span className="font-medium">{educationStats.attendingSchool}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Attending ECDC</span>
                <span className="font-medium">{educationStats.attendingECDC}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Attending REC</span>
                <span className="font-medium">{educationStats.attendingREC}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Has Extra Curriculars</span>
                <span className="font-medium">
                  {educationStats.hasExtraCurriculars}
                </span>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm">Has Academic Issues</span>
                <span className="font-medium">{educationStats.hasAcademicIssues}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Is Bullied</span>
                <span className="font-medium">{educationStats.isBullied}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Has Behavior Challenges</span>
                <span className="font-medium">
                  {educationStats.hasBehaviorChallenges}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Children Data Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Children Data</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Person ID</th>
                  <th className="text-left p-2">Case ID</th>
                  <th className="text-left p-2">Name</th>
                  <th className="text-left p-2">Age</th>
                  <th className="text-left p-2">Relation</th>
                  <th className="text-left p-2">Country</th>
                  <th className="text-left p-2">Education Level</th>
                </tr>
              </thead>
              <tbody>
                {children.map((child) => {
                  const age = currentYear - child.yearofbirth;
                  return (
                    <tr key={child.personid} className="border-b hover:bg-muted/50">
                      <td className="p-2">{child.personid}</td>
                      <td className="p-2">{child.caseid}</td>
                      <td className="p-2">
                        {child.firstname} {child.lastname}
                      </td>
                      <td className="p-2">{age}</td>
                      <td className="p-2">{child.relationtohead}</td>
                      <td className="p-2">{child.countryoforigin}</td>
                      <td className="p-2">{child.educationlevel}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

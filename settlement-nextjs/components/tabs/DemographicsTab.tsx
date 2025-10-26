"use client";

import { useState, useEffect } from "react";
import { JamatiMember } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function DemographicsTab() {
  const [members, setMembers] = useState<JamatiMember[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const res = await fetch("/api/members");
        const data = await res.json();
        setMembers(data.data || []);
      } catch (error) {
        console.error("Error fetching members:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return <div className="p-4">Loading demographics data...</div>;
  }

  // Calculate demographics
  const countryCount: Record<string, number> = {};
  const ageGroups: Record<string, number> = {
    "0-17": 0,
    "18-30": 0,
    "31-45": 0,
    "46-60": 0,
    "60+": 0,
  };
  const educationLevels: Record<string, number> = {};

  members.forEach((member) => {
    // Country counts
    countryCount[member.countryoforigin] =
      (countryCount[member.countryoforigin] || 0) + 1;

    // Age groups
    const age = new Date().getFullYear() - member.yearofbirth;
    if (age <= 17) ageGroups["0-17"]++;
    else if (age <= 30) ageGroups["18-30"]++;
    else if (age <= 45) ageGroups["31-45"]++;
    else if (age <= 60) ageGroups["46-60"]++;
    else ageGroups["60+"]++;

    // Education levels
    if (member.educationlevel) {
      educationLevels[member.educationlevel] =
        (educationLevels[member.educationlevel] || 0) + 1;
    }
  });

  const topCountries = Object.entries(countryCount)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Jamati Demographics</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Demographic analysis of jamati members in the settlement program.
          </p>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Country of Origin */}
        <Card>
          <CardHeader>
            <CardTitle>🌍 Country of Origin Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {topCountries.map(([country, count]) => (
                <div key={country} className="flex justify-between items-center">
                  <span className="text-sm">{country}</span>
                  <span className="font-medium">{count}</span>
                </div>
              ))}
            </div>
            <p className="text-xs text-muted-foreground mt-4">
              Chart visualization will be added with Recharts
            </p>
          </CardContent>
        </Card>

        {/* Age Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>📊 Age Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(ageGroups).map(([group, count]) => (
                <div key={group} className="flex justify-between items-center">
                  <span className="text-sm">{group} years</span>
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

      {/* Education Level */}
      <Card>
        <CardHeader>
          <CardTitle>🎓 Education Level Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(educationLevels).map(([level, count]) => (
              <div key={level} className="flex justify-between items-center">
                <span className="text-sm">{level}</span>
                <span className="font-medium">{count}</span>
              </div>
            ))}
          </div>
          <p className="text-xs text-muted-foreground mt-4">
            Chart visualization will be added with Recharts
          </p>
        </CardContent>
      </Card>

      {/* Member Data Table */}
      <Card>
        <CardHeader>
          <CardTitle>Jamati Member Data</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Person ID</th>
                  <th className="text-left p-2">Name</th>
                  <th className="text-left p-2">Age</th>
                  <th className="text-left p-2">Country</th>
                  <th className="text-left p-2">Education</th>
                  <th className="text-left p-2">English Fluency</th>
                </tr>
              </thead>
              <tbody>
                {members.slice(0, 50).map((member) => (
                  <tr key={member.personid} className="border-b hover:bg-muted/50">
                    <td className="p-2">{member.personid}</td>
                    <td className="p-2">
                      {member.firstname} {member.lastname}
                    </td>
                    <td className="p-2">
                      {new Date().getFullYear() - member.yearofbirth}
                    </td>
                    <td className="p-2">{member.countryoforigin}</td>
                    <td className="p-2">{member.educationlevel}</td>
                    <td className="p-2">{member.englishfluency}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {members.length > 50 && (
              <p className="mt-4 text-sm text-muted-foreground">
                Showing first 50 of {members.length} members
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

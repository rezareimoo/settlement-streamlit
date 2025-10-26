"use client";

import { useState, useEffect } from "react";
import { JamatiMember } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function MemberLookupTab() {
  const [members, setMembers] = useState<JamatiMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

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
    return <div className="p-4">Loading member data...</div>;
  }

  const filteredMembers = searchTerm
    ? members.filter(
        (m) =>
          m.firstname.toLowerCase().includes(searchTerm.toLowerCase()) ||
          m.lastname.toLowerCase().includes(searchTerm.toLowerCase()) ||
          m.caseid.toLowerCase().includes(searchTerm.toLowerCase()) ||
          m.personid.toString().includes(searchTerm)
      )
    : members;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Jamati Member Lookup</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">
            Search and view detailed information for any jamati member in the system.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>🔍 Search Members</CardTitle>
        </CardHeader>
        <CardContent>
          <input
            type="text"
            placeholder="Search by name, case ID, or person ID..."
            className="w-full border rounded-md p-2"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {searchTerm && (
            <p className="mt-2 text-sm text-muted-foreground">
              Found {filteredMembers.length} members matching "{searchTerm}"
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>📊 All Jamati Member Data</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Person ID</th>
                  <th className="text-left p-2">Case ID</th>
                  <th className="text-left p-2">First Name</th>
                  <th className="text-left p-2">Last Name</th>
                  <th className="text-left p-2">Age</th>
                  <th className="text-left p-2">Relation</th>
                  <th className="text-left p-2">Country</th>
                  <th className="text-left p-2">Education Level</th>
                  <th className="text-left p-2">English Fluency</th>
                </tr>
              </thead>
              <tbody>
                {filteredMembers.map((member) => {
                  const age = new Date().getFullYear() - member.yearofbirth;
                  return (
                    <tr key={member.personid} className="border-b hover:bg-muted/50">
                      <td className="p-2">{member.personid}</td>
                      <td className="p-2">{member.caseid}</td>
                      <td className="p-2">{member.firstname}</td>
                      <td className="p-2">{member.lastname}</td>
                      <td className="p-2">{age}</td>
                      <td className="p-2">{member.relationtohead}</td>
                      <td className="p-2">{member.countryoforigin}</td>
                      <td className="p-2">{member.educationlevel}</td>
                      <td className="p-2">{member.englishfluency}</td>
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

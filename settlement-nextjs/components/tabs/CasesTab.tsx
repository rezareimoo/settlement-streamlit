"use client";

import { useState, useEffect } from "react";
import { SettlementCase, JamatiMember, FDPCase } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type DataSource = "CMS" | "FDP" | "COMPARE";

export function CasesTab() {
  const [cases, setCases] = useState<SettlementCase[]>([]);
  const [members, setMembers] = useState<JamatiMember[]>([]);
  const [fdpCases, setFdpCases] = useState<FDPCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [dataSource, setDataSource] = useState<DataSource>("CMS");
  const [selectedRegion, setSelectedRegion] = useState<string>("All");
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const [casesRes, membersRes, fdpRes] = await Promise.all([
          fetch("/api/cases"),
          fetch("/api/members"),
          fetch("/api/fdp-cases"),
        ]);

        const casesData = await casesRes.json();
        const membersData = await membersRes.json();
        const fdpData = await fdpRes.json();

        setCases(casesData.data || []);
        setMembers(membersData.data || []);
        setFdpCases(fdpData.data || []);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return <div className="p-4">Loading cases data...</div>;
  }

  const regions = Array.from(new Set(cases.map((c) => c.region)));
  const filteredCases =
    selectedRegion === "All"
      ? cases
      : cases.filter((c) => c.region === selectedRegion);

  const totalCases = filteredCases.length;
  const openCases = filteredCases.filter(
    (c) => c.status === "Open" || c.status === "Reopen"
  ).length;
  const closedCases = filteredCases.filter((c) => c.status === "Closed").length;

  // Calculate regional summary
  const regionalSummary = regions.map((region) => {
    const regionCases = cases.filter((c) => c.region === region);
    const regionCaseIds = regionCases.map((c) => c.caseid);
    const regionMembers = members.filter((m) =>
      regionCaseIds.includes(m.caseid)
    );
    const regionOpen = regionCases.filter(
      (c) => c.status === "Open" || c.status === "Reopen"
    ).length;
    const regionClosed = regionCases.filter((c) => c.status === "Closed").length;

    return {
      region,
      cases: regionCases.length,
      individuals: regionMembers.length,
      open: regionOpen,
      closed: regionClosed,
    };
  });

  return (
    <div className="space-y-6">
      {/* Data Source Selection */}
      <Card>
        <CardHeader>
          <CardTitle>📊 Data Source Selection</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <Button
              variant={dataSource === "CMS" ? "default" : "outline"}
              onClick={() => setDataSource("CMS")}
            >
              CMS Data
            </Button>
            <Button
              variant={dataSource === "FDP" ? "default" : "outline"}
              onClick={() => setDataSource("FDP")}
            >
              FDP Data
            </Button>
            <Button
              variant={dataSource === "COMPARE" ? "default" : "outline"}
              onClick={() => setDataSource("COMPARE")}
            >
              Compare Both
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Date Filter */}
      <Card>
        <CardHeader>
          <CardTitle>Date Range Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Start Date</label>
              <input
                type="date"
                className="w-full border rounded p-2"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium">End Date</label>
              <input
                type="date"
                className="w-full border rounded p-2"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Region Filter */}
      <div className="flex items-center gap-4">
        <label className="font-medium">Select Region:</label>
        <Select value={selectedRegion} onValueChange={setSelectedRegion}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Select region" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="All">All</SelectItem>
            {regions.map((region) => (
              <SelectItem key={region} value={region}>
                {region}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Regional Summary Table */}
      <Card>
        <CardHeader>
          <CardTitle>🗺️ Regional Summary ({dataSource} Data)</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            This table summarizes the number of settlement cases, open cases,
            closed cases, and the aggregate number of individuals per region using{" "}
            {dataSource} data.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Region</th>
                  <th className="text-left p-2">Number of Cases</th>
                  <th className="text-left p-2">Number of Individuals</th>
                  <th className="text-left p-2">Open Cases</th>
                  <th className="text-left p-2">Closed Cases</th>
                </tr>
              </thead>
              <tbody>
                {regionalSummary.map((row) => (
                  <tr key={row.region} className="border-b">
                    <td className="p-2">{row.region}</td>
                    <td className="p-2">{row.cases.toLocaleString()}</td>
                    <td className="p-2">{row.individuals.toLocaleString()}</td>
                    <td className="p-2">{row.open.toLocaleString()}</td>
                    <td className="p-2">{row.closed.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Case Count Buttons */}
      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-4xl font-bold">{totalCases}</div>
              <div className="text-sm text-muted-foreground">Total Cases</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600">{openCases}</div>
              <div className="text-sm text-muted-foreground">Open Cases</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <Card>
        <CardHeader>
          <CardTitle>📊 Case Visualizations</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Chart visualizations will be implemented with Recharts in the next
            phase. This includes:
          </p>
          <ul className="list-disc list-inside mt-2 space-y-1 text-sm text-muted-foreground">
            <li>Case Status Distribution (Pie Chart)</li>
            <li>Cases by State (US Map)</li>
            <li>Case Status by Region (Stacked Bar Chart)</li>
            <li>New Cases Over Time by Region (Line Chart)</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}

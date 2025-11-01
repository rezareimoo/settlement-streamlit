"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CasesTab } from "@/components/tabs/CasesTab";
import { CaseLookupTab } from "@/components/tabs/CaseLookupTab";
import { MemberLookupTab } from "@/components/tabs/MemberLookupTab";
import { DemographicsTab } from "@/components/tabs/DemographicsTab";
import { ChildrenTab } from "@/components/tabs/ChildrenTab";

export default function Home() {
  return (
    <div className="w-full">
      <Tabs defaultValue="cases" className="w-full">
        <TabsList className="grid w-full grid-cols-5 mb-4">
          <TabsTrigger value="cases">
            Cases (CMS + FDP + Compare)
          </TabsTrigger>
          <TabsTrigger value="case-lookup">
            Case Lookup (CMS Only)
          </TabsTrigger>
          <TabsTrigger value="member-lookup">
            Jamati Member Lookup (CMS Only)
          </TabsTrigger>
          <TabsTrigger value="demographics">
            Jamati Demographics (CMS Only)
          </TabsTrigger>
          <TabsTrigger value="children">
            Children's Data (CMS Only)
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="cases">
          <CasesTab />
        </TabsContent>
        
        <TabsContent value="case-lookup">
          <CaseLookupTab />
        </TabsContent>
        
        <TabsContent value="member-lookup">
          <MemberLookupTab />
        </TabsContent>
        
        <TabsContent value="demographics">
          <DemographicsTab />
        </TabsContent>
        
        <TabsContent value="children">
          <ChildrenTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}

import TopBar from "@/components/layout/TopBar";
import DomainsView from "@/components/domains/DomainsView";

export default function DomainsPage() {
  return (
    <>
      <TopBar
        title="Domain Taxonomy"
        subtitle="Platform definitions, categories, and scoring dimensions"
      />
      <div className="flex-1 overflow-hidden flex flex-col">
        <DomainsView />
      </div>
    </>
  );
}

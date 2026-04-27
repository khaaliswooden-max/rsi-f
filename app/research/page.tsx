import TopBar from "@/components/layout/TopBar";
import ResearchView from "@/components/research/ResearchView";

export default function ResearchPage() {
  return (
    <>
      <TopBar
        title="Wofo Research"
        subtitle="N=12 filer roster, factor decomposition, and RSI self-improvement runs"
      />
      <div className="flex-1 overflow-hidden flex flex-col">
        <ResearchView />
      </div>
    </>
  );
}

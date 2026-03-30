import TopBar from "@/components/layout/TopBar";
import DashboardView from "@/components/dashboard/DashboardView";

export default function DashboardPage() {
  return (
    <>
      <TopBar
        title="Collection Dashboard"
        subtitle="Annotation progress across all Zuup domains"
      />
      <div className="flex-1 overflow-hidden flex flex-col">
        <DashboardView />
      </div>
    </>
  );
}

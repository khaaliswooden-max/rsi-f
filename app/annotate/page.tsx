import TopBar from "@/components/layout/TopBar";
import AnnotationView from "@/components/annotate/AnnotationView";

export default function AnnotatePage() {
  return (
    <>
      <TopBar
        title="Preference Annotation"
        subtitle="Label response pairs across Zuup domains"
      />
      <div className="flex-1 overflow-hidden">
        <AnnotationView />
      </div>
    </>
  );
}

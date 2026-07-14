import { AlertCircle } from "lucide-react";

interface AlertBadgeProps {
  count: number;
}

export default function AlertBadge({ count }: AlertBadgeProps) {
  return (
    <div className="flex items-center gap-2 bg-black/40 text-sm px-3 py-1 rounded-lg shadow-sm">
      <AlertCircle className="w-4 h-4 text-yellow-500/80" />
      <span>Alertas</span>
      {count > 0 ? (
        <span className="flex items-center bg-yellow-600 text-white text-xs font-medium px-1.5 rounded gap-1">
          <span>{count}</span>
        </span>
      ) : (
        <span className=" text-zinc-400 text-xs rounded-full px-2 py-1">０</span>
      )}
    </div>
  );
}

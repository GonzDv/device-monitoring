import type { Alert } from "../api";
import { AlertCircle, Clock } from "lucide-react";

interface AlertCardProps {
  alert: Alert;
}

export default function AlertCard({ alert }: AlertCardProps) {
  const isCritical = alert.severity?.toLowerCase() === "crítical";

  return (
    <div className="bg-[#161b26] border border-[#242c3d] rounded-xl p-5 shadow-lg  w-full font-sans text-slate-200 transition-all hover:border-slate-700">
      
      <div className="flex items-start gap-3 mb-4">
        <div className={`p-2 rounded-lg shrink-0 ${isCritical ? 'bg-red-500/10 text-red-400' : 'bg-amber-500/10 text-amber-400'}`}>
          <AlertCircle size={18} />
        </div>
        <div className="flex flex-col gap-0.5">
          <span className="text-[10px] font-bold tracking-wider uppercase opacity-40">
            Alerta
          </span>
          <h4 className={`text-base font-semibold leading-tight ${isCritical ? 'text-red-400' : 'text-amber-400'}`}>
            {alert.message}
          </h4>
        </div>
      </div>

      <div className="h-px bg-[#242c3d] my-3" />


      <div className="grid grid-cols-2 gap-y-3 gap-x-4 text-xs mb-4">
        <div>
          <span className="block text-slate-500 font-medium mb-0.5">Tipo:</span>
          <span className="font-semibold text-slate-300">{alert.alert_type}</span>
        </div>
        <div>
          <span className="block text-slate-500 font-medium mb-0.5">Severidad:</span>
          <span className={`font-semibold ${isCritical ? 'text-red-400' : 'text-amber-400'}`}>
            {alert.severity}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-[#242c3d]/50 text-xs">
        <div className="flex flex-col gap-1 text-slate-400">
          <div className="flex items-center gap-1.5 opacity-80">
            <Clock size={13} className="text-slate-500" />
            <span>Apertura:</span>
            <span className="font-medium text-slate-300">
              {alert.opened_at ? new Date(alert.opened_at).toLocaleString() : 'N/A'}
            </span>
          </div>
        </div>

        <div>
          {alert.state === "active" ? (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Abierta
            </span>
          ) : (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-[11px] font-semibold bg-slate-800 text-slate-400 border border-slate-700">
              Cerrada
            </span>
          )}
        </div>
      </div>

    </div>
  );
}
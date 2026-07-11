import type { Device, SnmpReadout } from "../api";
import { 
  Activity, 
  Box, 
  Loader2, 
  Monitor,
  Printer, 
  Server, 
  Trash2, 
  Wifi,
  Terminal,
  MapPin
} from "lucide-react";
import type { ReactNode } from "react";

interface DeviceCardProps {
  device: Device;
  isLoading: number | null;
  readout: SnmpReadout | null;
  onQuerySnmp: (id: number) => void;
  onEdit: (device: Device) => void;
  onDelete: (device: Device) => void;
}

export default function DeviceCard({
  device,
  isLoading,
  readout,
  onQuerySnmp,
  onEdit,
  onDelete,
}: DeviceCardProps) {
  const getDeviceIcon = (type: string): ReactNode => {
    switch (type.toLowerCase()) {
      case "router":
        return <Activity className="w-5 h-5 text-blue-400" />;
      case "switch":
        return <Server className="w-5 h-5 text-indigo-400" />;
      case "ap":
        return <Wifi className="w-5 h-5 text-emerald-400" />;
      case "printer":
        return <Printer className="w-5 h-5 text-zinc-400" />;
      case "ups":
        return <Monitor className="w-5 h-5 text-amber-400" />;
      default:
        return <Box className="w-5 h-5 text-zinc-500" />;
    }
  };

  return (
    <div className="group bg-zinc-900/40 border border-zinc-800/80 hover:border-zinc-700/80 p-5 rounded-xl transition-all duration-300 flex flex-col justify-between shadow-sm hover:shadow-md">
      <div>
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-zinc-950 rounded-lg border border-zinc-800/80">
              {getDeviceIcon(device.device_type)}
            </div>
            <div>
              <h3 className="text-base font-semibold text-zinc-100 group-hover:text-white transition-colors leading-tight">
                {device.name}
              </h3>
              <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-500 mt-1 block">
                {device.device_type}
              </span>
            </div>
          </div>
        </div>

        <div className="space-y-2 text-sm text-zinc-400 font-mono bg-zinc-950/50 p-3 rounded-lg border border-zinc-800/50">
          <p className="flex items-center gap-2">
            <Terminal className="w-3.5 h-3.5 text-zinc-500" />
            <span className="text-zinc-300">{device.ip_address}</span>
          </p>
          {device.location && (
            <p className="flex items-center gap-2">
              <MapPin className="w-3.5 h-3.5 text-zinc-500" />
              <span className="text-zinc-500 truncate">{device.location}</span>
            </p>
          )}
        </div>
      </div>

      <div className="mt-5 pt-5 border-t border-zinc-800/50 flex flex-col gap-3">
        <button
          onClick={() => onQuerySnmp(device.id)}
          disabled={isLoading === device.id}
          className="w-full bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors duration-200 flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {isLoading === device.id ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Consultando...
            </> 
          ) : (
            <>
              <Activity className="w-4 h-4" />
              Consultar SNMP
            </>
          )}
        </button>
        <button
          onClick={() => {
            onEdit(device);
          }}
          className="w-full bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/20 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors duration-200 flex items-center justify-center gap-2"
        >
          <Server className="w-4 h-4" />
          Editar Dispositivo
        </button>
        <button
          onClick={() => onDelete(device)}
          className="w-full bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors duration-200 flex items-center justify-center gap-2"
        >
          <Trash2 className="w-4 h-4" />
          Eliminar Dispositivo
        </button>

        {readout && readout.device_id === device.id && (
          <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800/80 text-xs font-mono space-y-2 animate-in fade-in duration-200 shadow-inner">
            <div className="text-zinc-500 pb-2 mb-2 border-b border-zinc-800/80 flex justify-between items-center">
              <span className="flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5" /> OUTPUT
              </span>
              <span className="text-emerald-400 flex items-center gap-1">
                ● OK
              </span>
            </div>
            <p className="text-zinc-300 flex flex-col gap-0.5">
              <span className="text-zinc-600 uppercase text-[10px] tracking-wider">
                SysName
              </span>{" "}
              {readout.snmp.sys_name}
            </p>
            <p
              className="text-zinc-300 flex flex-col gap-0.5 truncate"
              title={readout.snmp.sys_descr}
            >
              <span className="text-zinc-600 uppercase text-[10px] tracking-wider">
                Description
              </span>{" "}
              {readout.snmp.sys_descr}
            </p>
            <p className="text-zinc-300 flex flex-col gap-0.5">
              <span className="text-zinc-600 uppercase text-[10px] tracking-wider">
                Uptime
              </span>{" "}
              {readout.snmp.sys_uptime}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

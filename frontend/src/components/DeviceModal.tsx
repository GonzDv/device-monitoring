import {
  Activity,
  Server,
  X,

} from "lucide-react";
import Input from "../components/Input";
import type {  Device } from "../api";
import type { FormEvent } from "react";

interface DeviceModalProps {
  editingDevice: Device | null;
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
  onClose: () => void;
}

export default function DeviceModal({ editingDevice, onSubmit, onClose }: DeviceModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
            <div className="bg-zinc-900 border border-zinc-800/80 rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-200">
              <div className="flex justify-between items-center p-6 border-b border-zinc-800/60 bg-zinc-900">
                <h3 className="text-lg font-semibold text-zinc-100 flex items-center gap-2.5">
                  <Server className="w-5 h-5 text-zinc-400" />
                  {editingDevice ? "Editar Dispositivo" : "Agregar Dispositivo"}
                </h3>
                <button
                  onClick={onClose}
                  className="text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 p-1.5 rounded-lg transition-colors focus:outline-none"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div>
                
              </div>

              <form className="p-6 space-y-5" onSubmit={onSubmit}>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <Input
                      label="Nombre del Equipo"
                      type="text"
                      name="name"
                      placeholder="ej. Switch-Core-01"
                      required
                      defaultValue={editingDevice ? editingDevice.name : ""}
                    />
                    <Input
                      label="Dirección IPv4"
                      type="text"
                      name="ip_address"
                      placeholder="192.168.1.1"
                      defaultValue={
                        editingDevice ? editingDevice.ip_address : ""
                      }
                      required
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <Input
                      label="Tipo de Dispositivo"
                      type="select"
                      name="device_type"
                      defaultValue={
                        editingDevice ? editingDevice.device_type : ""
                      }
                      required
                      options={[
                        { value: "switch", label: "Switch de Red" },
                        { value: "router", label: "Enrutador" },
                        { value: "ap", label: "Punto de Acceso" },
                        { value: "printer", label: "Impresora" },
                        { value: "ups", label: "Sistema UPS" },
                        { value: "other", label: "Otro" },
                      ]}
                    />
                    <Input
                      label="Ubicación Física"
                      type="text"
                      name="location"
                      defaultValue={editingDevice?.location ?? ""}
                      placeholder="Rack Principal"
                    />
                  </div>
                </div>

                <div className="bg-zinc-950/40 p-5 rounded-xl border border-zinc-800/60 space-y-4">
                  <div className="flex items-center gap-2 text-sm font-semibold text-zinc-300">
                    <Activity className="w-4 h-4 text-zinc-500" />
                    Parámetros SNMP
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <Input
                      label="Versión"
                      type="select"
                      name="snmp_version"
                      defaultValue={
                        editingDevice ? editingDevice.snmp_version : "v2c"
                      }
                      options={[
                        { value: "v1", label: "SNMP v1" },
                        { value: "v2c", label: "SNMP v2c" },
                        { value: "v3", label: "SNMP v3" },
                      ]}
                    />
                    <Input
                      label="Puerto UDP"
                      type="number"
                      name="snmp_port"
                      defaultValue={
                        editingDevice ? String(editingDevice.snmp_port) : "161"
                      }
                      placeholder="161"
                    />
                  </div>
                  <Input
                    label="Comunidad"
                    type="text"
                    name="snmp_community"
                    defaultValue={
                      editingDevice
                        ? editingDevice.snmp_community || "public"
                        : ""
                    }
                    placeholder="Dejar vacío para no cambiar"
                  />
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t border-zinc-800/60">
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-4 py-2.5 rounded-lg text-sm font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium bg-zinc-100 text-zinc-900 hover:bg-white transition-colors shadow-sm active:scale-95"
                  >
                  {editingDevice ? "Actualizar Dispositivo" : "Agregar Dispositivo"}
                  </button>
                </div>
              </form>
            </div>
          </div>
  )
}
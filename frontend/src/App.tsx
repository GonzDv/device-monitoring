import { useEffect, useState, type FormEvent } from "react";

import DeviceCard from "./components/DeviceCard";
import { Activity, Plus, X, AlertCircle, AlertTriangle, RefreshCw } from "lucide-react";
import {
  getDevices,
  createDevice,
  queryDeviceSnmp,
  updateDevice,
  deleteDevice,
  getAlerts,
  type DeviceCreate,
  type Device,
  type SnmpReadout,
  type Alert,
} from "./api";
import DeviceModal from "./components/DeviceModal";
import AlertBadge from "./components/AlertBadge";
import AlertCard from "./components/AlertCard";

function App() {
  const [error, setError] = useState<string | null>(null);
  const [devices, setDevices] = useState<Device[]>([]);
  const [readout, setReadout] = useState<SnmpReadout | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState<number | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);

  const openModal = () => setIsOpen(true);
  const closeModal = () => setIsOpen(false);

  const [editingDevice, setEditingDevice] = useState<Device | null>(null);

  useEffect(() => {
    getAlerts()
      .then((data) => setAlerts(data))
      .catch((err) => setError(String(err)));
    getDevices()
      .then((devices: Device[]) => {
        setDevices(devices);
      })
      .catch((err) => setError(String(err)));
  }, []);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const formData = new FormData(form);
    const snmpPort = formData.get("snmp_port") as string;

    const deviceData: Partial<DeviceCreate> = {
      name: formData.get("name") as string,
      ip_address: (formData.get("ip_address") as string).trim(),
      device_type: formData.get("device_type") as string,
      location: formData.get("location") as string,
      snmp_version: formData.get("snmp_version") as string,
      snmp_port: Number(snmpPort) || 161,
      snmp_community:
        (formData.get("snmp_community") as string)?.trim() || null,
    };

    try {
      if (editingDevice) {
        if (!deviceData.snmp_community) {
          delete deviceData.snmp_community;
        }
        await updateDevice(editingDevice.id, deviceData);
      } else {
        const created = await createDevice(deviceData as DeviceCreate);
        setDevices([created, ...devices]);
      }
      closeModal();
      setEditingDevice(null);
      const fresh = await getDevices();
      setDevices(fresh);
    } catch (err) {
      setError(String(err));
    }
  };

  const handleQuerySnmp = async (deviceId: number) => {
    try {
      setIsLoading(deviceId);
      const snmpData = await queryDeviceSnmp(deviceId);
      setReadout(snmpData);
    } catch (err) {
      setError(String(err));
    } finally {
      setIsLoading(null);
    }
  };

  const handleEdit = (device: Device) => {
    setEditingDevice(device);
    openModal();
  };

  const handleDelete = (device: Device) => {
    if (confirm(`¿Eliminar ${device.name}?`)) {
      deleteDevice(device.id)
        .then(() => {
          setDevices(devices.filter((d) => d.id !== device.id));
          if (readout && readout.device_id === device.id) {
            setReadout(null);
          }
        })
        .catch((err) => setError(String(err)));
    }
  };
  const handleGetAlerts = async () => {
    alerts && setAlerts([]);
    try {
      const alertsData = await getAlerts();
      setAlerts(alertsData);
      console.log(alertsData);
    } catch (err) {
      setError(String(err));
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 font-sans antialiased selection:bg-zinc-800">
      <div className="max-w-5xl mx-auto p-6 md:p-12">
        <header className="flex justify-between items-center pb-6 mb-8 border-b border-zinc-800/80">
          <div className="flex items-center gap-4">
            <div className="p-2.5 bg-zinc-900 rounded-xl border border-zinc-800 shadow-sm">
              <Activity className="w-6 h-6 text-zinc-100" />
            </div>
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-white">
                Infraestructura & Redes
              </h1>
              <p className="text-sm text-zinc-400 mt-1">
                Monitorización de dispositivos y lecturas SNMP en tiempo real.
              </p>
            </div>
          </div>
          <div>
            <AlertBadge count={alerts.length} />
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={openModal}
              className="flex items-center gap-2 bg-zinc-100 text-zinc-900 px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-white transition-all duration-200 shadow-sm active:scale-95"
            >
              <Plus className="w-4 h-4" /> Agregar Dispositivo
            </button>
          </div>
        </header>
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-zinc-100">
            Alertas Activas
          </h2>
        </div>
        <div className="w-full mb-6 flex items-center justify-between gap-3">
          {alerts.map((alert) => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-950/40 border border-red-900/50 text-red-300 text-sm flex justify-between items-start shadow-sm animate-in fade-in">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
              <div>
                <strong className="block text-red-200 mb-0.5">
                  Error del sistema
                </strong>
                <span>{error}</span>
              </div>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-red-500 hover:text-red-300 transition-colors p-1"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {devices.map((device) => (
            <DeviceCard
              key={device.id}
              device={device}
              isLoading={isLoading}
              readout={readout}
              onQuerySnmp={handleQuerySnmp}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))}
        </div>
        {isOpen && (
          <DeviceModal
            editingDevice={editingDevice}
            onSubmit={handleSubmit}
            onClose={() => {
              closeModal();
              setEditingDevice(null);
            }}
          />
        )}
      </div>
    </div>
  );
}

export default App;

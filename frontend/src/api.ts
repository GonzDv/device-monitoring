const BASE_URL = import.meta.env.VITE_API_URL;

export interface Device {
  id: number;
  name: string;
  ip_address: string;
  device_type: string;
  location?: string | null;
  snmp_version: string;
  snmp_port: number;
  snmp_community: string | null;
  status: "up" | "down" | "unknown";
  last_seen_at: string | null;
  created_at: string;
}

async function getDevices(): Promise<Device[]> {
  const response = await fetch(`${BASE_URL}/devices`);
  if (!response.ok) {
    throw new Error(`Error fetching devices: ${response.statusText}`);
  }
  return response.json();
}

export interface DeviceCreate {
  name: string;
  ip_address: string;
  device_type: string;
  location: string | null;
  snmp_version: string;
  snmp_port: number;
  snmp_community: string | null;
}

async function createDevice(device: DeviceCreate): Promise<Device> {
  const response = await fetch(`${BASE_URL}/devices`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(device),
  });

  if (!response.ok) {
    throw new Error(` creating device: ${response.statusText}`);
  }
  return response.json();
}

async function updateDevice(id: number, device: Partial<DeviceCreate>): Promise<Device> {
  const response = await fetch(`${BASE_URL}/devices/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(device),
  });

  if (!response.ok) {
    throw new Error(`Error updating device: ${response.statusText}`);
  }
  return response.json();
}

async function deleteDevice(id: number): Promise<void> {
  const response = await fetch(`${BASE_URL}/devices/${id}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error(`Error deleting device: ${response.statusText}`);
  }
}

export interface SnmpReadout {
  device_id: number;
  name: string;
  ip_address: string;
  snmp: {
    sys_name: string;
    sys_descr: string;
    sys_uptime: string;
    sys_location: string;
  };
}

async function queryDeviceSnmp(id: number): Promise<SnmpReadout   > {
  const response = await fetch(`${BASE_URL}/devices/${id}/snmp`);
  if (!response.ok) {
    throw new Error(`Error fetching device by ID: ${response.statusText}`);
  }
  return response.json();
}

export { getDevices, createDevice, queryDeviceSnmp, updateDevice, deleteDevice };
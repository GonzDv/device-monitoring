import { useEffect, useState } from "react"

function App() {
  const [status, setStatus] = useState<string>("cargando...")
  const [rows, setRows] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch("http://localhost:8000/db-check")
      .then((res) => res.json())
      .then((data) => {
        setStatus(data.db)
        setRows(data.ping_log_rows)
      })
      .catch((err) => setError(String(err)))
  }, [])

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-slate-800">DeviceMonitoring</h1>
      <p className="mt-2 text-slate-500">Panel de monitoreo SNMP — Sprint 0</p>

      <div className="mt-6 rounded-lg border border-slate-200 p-4 w-fit">
        <h2 className="text-lg font-semibold text-slate-700">Estado del backend</h2>
        {error ? (
          <p className="mt-1 text-red-600">Error: {error}</p>
        ) : (
          <p className="mt-1 text-slate-600">
            Base de datos:{" "}
            <span className="font-mono font-bold text-green-600">{status}</span>
            {rows !== null && (
              <> · filas en ping_log: <span className="font-mono">{rows}</span></>
            )}
          </p>
        )}
      </div>
    </div>
  )
}

export default App
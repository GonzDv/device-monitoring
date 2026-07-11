// Input.tsx
interface InputProps {
  label: string;
  type?: string;
  name: string;
  defaultValue?: string;
  placeholder?: string;
  options?: { value: string; label: string }[];
  required?: boolean;
}

export default function Input({
  label,
  type = "text",
  name,
  options,
  defaultValue,
  placeholder,
  required
}: InputProps) {
  const baseClasses = "w-full bg-zinc-950/50 border border-zinc-800 rounded-lg px-3.5 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 transition-all duration-200 shadow-sm";

  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={name} className="text-sm font-medium text-zinc-400 ml-0.5">
        {label}
      </label>

      {type === "select" ? (
        <select
          name={name}
          defaultValue={defaultValue}
          required={required}
          className={`${baseClasses} appearance-none cursor-pointer`}
        >
          <option value="" className="bg-zinc-900 text-zinc-500">
            Seleccione una opción
          </option>
          {options?.map((opt) => (
            <option key={opt.value} value={opt.value} className="bg-zinc-900 text-zinc-200">
              {opt.label}
            </option>
          ))}
        </select>
      ) : (
        <input
          defaultValue={defaultValue}
          placeholder={placeholder}
          required={required}
          type={type}
          name={name}
          className={baseClasses}
        />
      )}
    </div>
  );
}
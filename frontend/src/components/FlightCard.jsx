export default function FlightCard({ flight }) {
  if (!flight) return null;

  const flights = Array.isArray(flight.flights)
    ? flight.flights
    : [flight.flight_number || flight.flight ? { ...flight, flight_number: flight.flight_number || flight.flight } : null];

  return flights.filter(Boolean).map((item) => (
    <div
      key={item.flight_number}
      className="mt-4 rounded-2xl border border-sky-500/30 bg-slate-900/90 p-4 shadow-soft"
    >
      <div className="mb-3 flex items-center justify-between gap-3">
        <div>
          <div className="text-xs uppercase tracking-[0.18em] text-sky-300">✈ Flight</div>
          <h4 className="text-xl font-semibold text-white">
            {item.airline} {item.flight_number}
          </h4>
        </div>
        <div className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-sm text-emerald-300">
          {item.status}
        </div>
      </div>

      <div className="text-lg font-medium text-slate-100">
        {item.source} → {item.destination}
      </div>

      {item.data_source && (
        <div className="mt-1 text-xs text-slate-400">
          {item.data_source === 'sample_data'
            ? 'Sample data, not live'
            : item.data_source.startsWith('sample_data:')
              ? item.data_source.slice('sample_data:'.length).trim()
              : item.data_source}
        </div>
      )}

      <div className="mt-3 grid grid-cols-2 gap-3 text-sm text-slate-300">
        <div>
          <div className="text-slate-400">Departure</div>
          <div>{item.departure}</div>
        </div>
        <div>
          <div className="text-slate-400">Arrival</div>
          <div>{item.arrival}</div>
        </div>
      </div>

      {item.price != null && (
        <div className="mt-4 flex items-center justify-between border-t border-slate-700 pt-3 text-slate-100">
          <span className="text-slate-400">Price</span>
          <span className="text-xl font-bold text-amber-300">
            ₹{item.price.toLocaleString()}
          </span>
        </div>
      )}
    </div>
  ));
}

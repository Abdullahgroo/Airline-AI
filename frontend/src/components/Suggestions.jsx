export default function Suggestions({ onSelect }) {
  const suggestions = [
    'Find flights from Delhi to Paris',
    "What's the price of a flight from Delhi to Paris?",
    'Check flight AI202',
    'What is the baggage allowance?',
    'What documents do I need for travel?',
  ];

  return (
    <div className="mb-4">
      <div className="text-xs uppercase tracking-[0.18em] text-slate-400 mb-2">Suggested</div>
      <div className="flex flex-wrap gap-2">
        {suggestions.map((item) => (
          <button
            key={item}
            onClick={() => onSelect(item)}
            className="rounded-full border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 transition hover:border-sky-400 hover:text-sky-300"
          >
            {item}
          </button>
        ))}
      </div>
    </div>
  );
}

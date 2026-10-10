export default function Message({ message }) {
  const isUser = message.sender === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className="max-w-[80%]">
        <div
          className={`rounded-2xl px-4 py-3 shadow-soft ${
            isUser
              ? 'bg-skyBrand text-white rounded-br-md'
              : 'bg-slate-800 text-slate-100 rounded-bl-md border border-slate-700'
          }`}
        >
          <div className="text-xs uppercase tracking-wide mb-1 opacity-80">
            {isUser ? 'You' : 'Airline AI'}
          </div>
          <div className="whitespace-pre-wrap break-words">{message.text}</div>
        </div>

        {!isUser && (message.provider || message.dataSource) && (
          <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 px-2 text-xs text-slate-400">
            {message.provider && <span>Answered by {message.provider}</span>}
            {message.dataSource && <span>Flight data: {message.dataSource}</span>}
          </div>
        )}
      </div>
    </div>
  );
}

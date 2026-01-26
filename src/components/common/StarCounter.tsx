interface StarCounterProps {
  stars: number;
  total?: number;
  size?: 'small' | 'medium' | 'large';
}

export default function StarCounter({ stars, total, size = 'medium' }: StarCounterProps) {
  const sizeClasses = {
    small: 'text-xl gap-1',
    medium: 'text-3xl gap-2',
    large: 'text-5xl gap-3',
  };

  return (
    <div className={`flex items-center ${sizeClasses[size]}`}>
      <span className="animate-bounce" style={{ animationDelay: '0ms' }}>⭐</span>
      <span className="font-bold text-yellow-400 drop-shadow-lg">
        {stars}
        {total !== undefined && (
          <span className="text-white/70">/{total}</span>
        )}
      </span>
    </div>
  );
}

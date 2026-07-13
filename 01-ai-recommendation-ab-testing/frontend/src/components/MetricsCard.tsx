interface Props {
  title: string;
  value: string | number;
  subtitle?: string;
  highlight?: boolean;
}

export default function MetricsCard({ title, value, subtitle, highlight }: Props) {
  return (
    <div className={`metrics-card ${highlight ? "highlight" : ""}`}>
      <h3>{title}</h3>
      <div className="metrics-value">{value}</div>
      {subtitle && <div className="metrics-subtitle">{subtitle}</div>}
    </div>
  );
}

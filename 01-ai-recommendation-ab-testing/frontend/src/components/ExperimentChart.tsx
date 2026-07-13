import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { VariantMetrics } from "../api/types";

interface Props {
  variants: VariantMetrics[];
}

export default function ExperimentChart({ variants }: Props) {
  const data = variants.map((v) => ({
    name: `Variant ${v.variant}`,
    CTR: parseFloat((v.ctr * 100).toFixed(2)),
    "Conversion Rate": parseFloat((v.conversion_rate * 100).toFixed(2)),
    "Revenue per User": parseFloat(v.revenue_per_user.toFixed(2)),
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="CTR" fill="#8884d8" />
        <Bar dataKey="Conversion Rate" fill="#82ca9d" />
        <Bar dataKey="Revenue per User" fill="#ffc658" />
      </BarChart>
    </ResponsiveContainer>
  );
}
